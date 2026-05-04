import math
from datetime import datetime, timedelta

import cloudinary.uploader
from flask_login import login_user, logout_user, current_user
from werkzeug.utils import redirect
from ecourse import login_manager, db
from ecourse.config import NGAY_BAT_DAU_DANG_KY, NGAY_BAT_DAU_HK, TIN_CHI_TOI_THIEU, HAN_DANG_KY
from flask import render_template, session
from ecourse.models import LopHocPhan, DangKy, HocKy
from ecourse import app, dao
from flask_login import login_required
from flask import request, jsonify


def register_route(app):
    @app.route("/")
    def index():
        # ràng buộc Không được đăng ký môn sau thời hạn đăng ký
        het_han_dang_ky = False
        if datetime.now() > HAN_DANG_KY:
            het_han_dang_ky = True

        page = request.args.get("page", 1, type=int)
        kw = request.args.get("kw")
        pages = math.ceil(dao.count_lop_hoc_phan() / app.config['PAGE_SIZE'])
        classes = dao.load_lop_hoc_phan(kw=kw, page=page)
        return render_template("index.html",
                               het_han_dang_ky=het_han_dang_ky,
                               NGAY_BAT_DAU_DANG_KY=NGAY_BAT_DAU_DANG_KY,
                               HAN_DANG_KY=HAN_DANG_KY,
                               TIN_CHI_TOI_THIEU=TIN_CHI_TOI_THIEU,
                               classes=classes,
                               pages=pages,
                               curent_page=page)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        error_msg = None
        if request.method.__eq__("POST"):
            username = request.form.get("username")
            password = request.form.get("password")
            user = dao.auth_user(username, password)
            if user:
                login_user(user)
                next = request.args.get("next")
                return redirect(next if next else "/")
            else:
                error_msg = "Đăng nhập không thành công. Vui lòng kểm tra lại username và mật khẩu"

        return render_template("login.html", error_msg=error_msg)


    @app.route("/logout")
    def logout():
        logout_user()
        session.pop('cart', None)
        return redirect("/")

    @app.route('/api/dang_ky_tam', methods=['POST'])
    @login_required
    def api_dang_ky_tam():
        cart = session.get('cart', {})
        data = request.json
        #Chặn ghi danh lớp active
        new_id = str(data.get('id'))
        lop_check = LopHocPhan.query.get(new_id)

        if not lop_check:
            return jsonify({'status': 400, 'err_msg': 'Lớp học phần không tồn tại trên hệ thống!'})
        if not lop_check.active:
            return jsonify({'status': 400, 'err_msg': 'Lớp học phần này hiện đã bị khóa hoặc không mở đăng ký!'})

        hoc_ky_check = HocKy.query.get(lop_check.hoc_ky_id)
        if not hoc_ky_check or not hoc_ky_check.active:
            return jsonify(
                {'status': 400, 'err_msg': 'Học kỳ của môn này hiện không trong thời gian cho phép đăng ký!'})

        new_name = data.get('name')
        new_thu = str(data.get('thu'))
        new_ca = str(data.get('ca_hoc'))

        if new_id in cart:
            return jsonify({'status': 400, 'err_msg': 'Môn này đã có trong danh sách!'})

        for item in cart.values():
            if str(item['thu']) == new_thu and str(item['ca_hoc']) == new_ca:
                return jsonify({
                    'status': 400,
                    'err_msg': f'Trùng lịch! Thứ {new_thu} - Ca {new_ca} bạn đã chọn môn {item["name"]}.'
                })

        ds_da_dang_ky = DangKy.query.filter_by(sinh_vien_id=current_user.id).all()
        for dk in ds_da_dang_ky:
            lop_da_dk = dk.lop_hoc_phan

            if str(lop_da_dk.thu) == new_thu and str(lop_da_dk.ca_hoc) == new_ca:
                return jsonify({
                    'status': 400,
                    'err_msg': f'Trùng lịch! Thứ {new_thu} - Ca {new_ca} bạn đã có lịch học môn {lop_da_dk.mon_hoc.name}.'
                })

            if str(lop_da_dk.mon_hoc_id) == str(lop_check.mon_hoc_id):
                return jsonify({
                    'status': 400,
                    'err_msg': f'Bạn đã xác nhận đăng ký môn {lop_da_dk.mon_hoc.name} này rồi!'
                })
        cart[new_id] = {
            "id": new_id,
            "name": new_name,
            "tin_chi": data.get('tin_chi'),
            "thu": new_thu,
            "ca_hoc": new_ca,
            "phong_hoc": data.get('phong_hoc')
        }
        session['cart'] = cart

        return jsonify({'status': 200, 'message': 'Đã thêm vào danh sách chờ'})

    @app.route("/api/xoa-mon-tam/<id>", methods=['DELETE'])
    @login_required
    def api_xoa_mon_tam(id):
        cart = session.get('cart', {})
        if id in cart:
            del cart[id]
            session['cart'] = cart
            return jsonify({'status': 200, 'message': 'Đã xóa thành công'})
        return jsonify({'status': 400, 'err_msg': 'Môn học không tồn tại trong danh sách'})

    @app.route("/api/xoa_mon_da_dang_ky/<int:id>", methods=['DELETE'])
    @login_required
    def api_xoa_mon_da_dang_ky(id):
        #Không được hủy sau 2 tuần
        if datetime.now() > NGAY_BAT_DAU_HK + timedelta(weeks=2):
            return jsonify({'status': 400, 'message': 'Quá thời hạn 2 tuần để hủy môn!'})

        phieu_dk = DangKy.query.get(id)

        if not phieu_dk:
            return jsonify({'status': 404, 'message': 'Không tìm thấy dữ liệu đăng ký này!'})

        # Chỉ sinh viên đăng ký mới được huỷ
        if phieu_dk.sinh_vien_id != current_user.id:
            return jsonify({'status': 403, 'message': 'Không có quyền hủy!'})

        ds_da_dk = DangKy.query.filter_by(sinh_vien_id=current_user.id).all()
        tong_tc_hien_tai = sum(dk.lop_hoc_phan.mon_hoc.so_tin_chi for dk in ds_da_dk)
        tc_mon_xoa = phieu_dk.lop_hoc_phan.mon_hoc.so_tin_chi
        if (tong_tc_hien_tai - tc_mon_xoa) < 12:
            return jsonify({
                'status': 400,
                'message': f'Quy định tối thiểu 12 TC. Hiện tại bạn có {tong_tc_hien_tai} TC, xóa môn này sẽ không đủ điều kiện.'
            })

        # Kiểm tra đã thi giữa kỳ chưa
        if phieu_dk.lop_hoc_phan.da_thi_giua_ky:
            return jsonify({'status': 400, 'message': 'Môn đã có điểm giữa kỳ, không thể hủy!'})

        db.session.delete(phieu_dk)
        db.session.commit()
        return jsonify({'status': 200, 'message': 'Hủy môn thành công!'})

    @app.route("/class_register")
    @login_required
    def class_register():
        cart = session.get('cart', {})
        lop_cho = list(cart.values()) if cart else []
        tong_tc = sum(int(item['tin_chi']) for item in lop_cho)
        danhSachMonDaDangKy = DangKy.query.filter_by(sinh_vien_id=current_user.id).all()
        for mon in danhSachMonDaDangKy:
            tong_tc += mon.lop_hoc_phan.mon_hoc.so_tin_chi
        history_data = dao.get_registered_classes(current_user.id)

        # rang buoc huy mon sau 2 tuan hoc
        huy_mon = True
        if datetime.now() > NGAY_BAT_DAU_HK + timedelta(weeks=2):
            huy_mon = False

        return render_template('class_register.html',
                               lop_cho=lop_cho,
                               tong_tc=tong_tc,
                               history=history_data,
                               huy_mon=huy_mon,
                               TIN_CHI_TOI_THIEU=TIN_CHI_TOI_THIEU)

    @app.route('/timetable')
    @login_required
    def timetable():
        ds_dang_ky = DangKy.query.filter_by(sinh_vien_id=current_user.id).all()
        lop_da_xac_nhan = [dk.lop_hoc_phan for dk in ds_dang_ky]
        return render_template('timetable.html', lop_da_xac_nhan=lop_da_xac_nhan)

    @app.route('/api/checkout', methods=['POST'])
    @login_required
    def checkout():
        cart = session.get('cart', {})
        if not cart:
            return jsonify({'status': 400, 'message': 'Danh sách đang trống!'})
        lop_cho = list(cart.values())
        tong_tc = sum(int(item['tin_chi']) for item in lop_cho)

        danhSachMonDaDangKy = DangKy.query.filter_by(sinh_vien_id=current_user.id).all()
        for mon in danhSachMonDaDangKy:
            tong_tc += mon.lop_hoc_phan.mon_hoc.so_tin_chi

        if tong_tc < 12:
            return jsonify({'status': 400, 'message': 'Bạn chưa chọn đủ 12 tín chỉ!'})
        ds_loi = []
        try:
            for item in lop_cho:
                lop_id = int(item['id'])

                try:
                    dao.dang_ky_lop(lop_id)
                except Exception as e:
                    ds_loi.append(f"- Môn {item['name']}: {str(e)}")

            if ds_loi:
                db.session.rollback()
                loi_str = "\n".join(ds_loi)
                return jsonify({
                    'status': 400,
                    'message': f'Xác nhận thất bại do vi phạm ràng buộc:\n{loi_str}'
                })
            else:
                db.session.commit()
                session.pop('cart', None)
                session.modified = True
                return jsonify({'status': 200, 'message': 'Đăng ký thành công toàn bộ môn học!'})

        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 500, 'message': 'Lỗi hệ thống: ' + str(e)})


@app.route("/register", methods=["GET", "POST"])
def register():
    error_msg = None
    if request.method.__eq__("POST"):
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        if password.__eq__(confirm):

            name = request.form.get('name')
            username = request.form.get("username")
            avatar = request.files.get('avatar')
            file_path = None

            if dao.get_user_by_username(username):
                error_msg = "Trùng username"
            else:
                if avatar:
                    res = cloudinary.uploader.upload(avatar)
                    file_path = res['secure_url']

                try:
                    dao.add_user(name, username, password, avatar=file_path)
                    return redirect('/login')
                except Exception as e:
                    db.session.rollback()
                    error_msg = "Hệ thống đang bị lỗi! Vui lòng quay lại sau!"
        else:
            error_msg = "Mật khẩu không khớp!"

    return render_template("register.html", error_msg=error_msg)


@app.route("/user_information")
@login_required
def user_information():
    user_information = dao.get_registered_classes(current_user.id)
    return render_template("user_information.html", user_information=user_information)


@app.context_processor
def common_data():
    if current_user.is_authenticated:
        registered_ids = [dk.lop_hoc_phan_id for dk in current_user.ds_dang_ky]
    else:
        registered_ids = []

    return dict(registered_ids=registered_ids)


@login_manager.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id=user_id)


if __name__ == "__main__":
    from ecourse import admin
    register_route(app=app)
    app.run(debug=True)
