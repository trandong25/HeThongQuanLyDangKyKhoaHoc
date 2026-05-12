import math
from datetime import datetime, timedelta
import cloudinary.uploader
from flask_login import login_user, logout_user, current_user
from werkzeug.utils import redirect
from ecourse import login_manager, db
from ecourse.config import NGAY_BAT_DAU_DANG_KY, NGAY_BAT_DAU_HK, TIN_CHI_TOI_THIEU, HAN_DANG_KY, TIN_CHI_TOI_DA, \
    HAN_HUY_MON
from flask import render_template, session
from ecourse.dao import get_hoc_ky_by_id
from ecourse.models import  DangKy
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
        pages = math.ceil(dao.count_lop_hoc_phan(kw=kw) / app.config['PAGE_SIZE'])
        classes = dao.load_lop_hoc_phan(kw=kw, page=page)
        return render_template("index.html",
                               het_han_dang_ky=het_han_dang_ky,
                               NGAY_BAT_DAU_DANG_KY=NGAY_BAT_DAU_DANG_KY,
                               HAN_DANG_KY=HAN_DANG_KY,
                               TIN_CHI_TOI_THIEU=TIN_CHI_TOI_THIEU,
                               TIN_CHI_TOI_DA=TIN_CHI_TOI_DA,
                               classes=classes,
                               pages=pages,
                               current_page=page)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect("/")
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
        return redirect("/login")

    @app.route('/api/dang_ky_tam', methods=['POST'])
    @login_required
    def api_dang_ky_tam():
        cart = session.get('cart', {})
        data = request.json
        # Chặn ghi danh lớp active
        new_id = str(data.get('id'))

        lop_check = dao.get_lop_hoc_phan_by_id(new_id)
        if not lop_check:
            return jsonify({'status': 400, 'err_msg': 'Lớp học phần không tồn tại trên hệ thống!'})
        if not lop_check.active:
            return jsonify({'status': 400, 'err_msg': 'Lớp học phần này hiện đã bị khóa hoặc không mở đăng ký!'})

        hoc_ky_check = get_hoc_ky_by_id(lop_check.hoc_ky_id)
        if not hoc_ky_check or not hoc_ky_check.active:
            return jsonify(
                {'status': 400, 'err_msg': 'Học kỳ của môn này hiện không trong thời gian cho phép đăng ký!'})

        new_name = data.get('name')
        new_thu = str(data.get('thu'))
        new_ca = str(data.get('ca_hoc'))

        # đăng ký trùng môn, trùng môn nhưng khác lịch học
        for item in cart.values():
            if str(item.get('mon_hoc_id')) == str(lop_check.mon_hoc_id):
                return jsonify({
                    'status': 400,
                    'err_msg': f'Môn này đã có trong danh sách !'
                })

        # trùng lịch học
        for item in cart.values():
            if str(item['thu']) == new_thu and str(item['ca_hoc']) == new_ca:
                return jsonify({
                    'status': 400,
                    'err_msg': f'Trùng lịch! Thứ {new_thu} - Ca {new_ca} bạn đã chọn môn {item["name"]}.'
                })

        # kiểm tra môn đã đăng ký rồi
        ds_da_dang_ky = dao.get_registered_classes(current_user.id)
        for ds in ds_da_dang_ky:
            lop_da_dang_ky = ds.lop_hoc_phan

            # kiểm tra trùng lich
            if str(lop_da_dang_ky.thu) == new_thu and str(lop_da_dang_ky.ca_hoc) == new_ca:
                return jsonify({
                    'status': 400,
                    'err_msg': f'Trùng lịch! Thứ {new_thu} - Ca {new_ca} bạn đã có lịch học môn {lop_da_dang_ky.mon_hoc.name}.'
                })

            # kiểm tra trùng môn
            if str(lop_da_dang_ky.mon_hoc_id) == str(lop_check.mon_hoc_id):
                return jsonify({
                    'status': 400,
                    'err_msg': f'Bạn đã xác nhận đăng ký môn {lop_da_dang_ky.mon_hoc.name} này rồi!'
                })

        # thêm vào giỏ tạm
        cart[new_id] = {
            "id": new_id,
            "name": new_name,
            "mon_hoc_id": str(lop_check.mon_hoc_id),
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

            session.modified = True
            return jsonify({'status': 200, 'message': 'Đã xóa thành công'})
        return jsonify({'status': 400, 'err_msg': 'Môn học không tồn tại trong danh sách'})

    @app.route("/api/xoa_mon_da_dang_ky/<int:id>", methods=['DELETE'])
    @login_required
    def api_xoa_mon_da_dang_ky(id):
        # Không được hủy sau 2 tuần
        if datetime.now() > HAN_HUY_MON:
            return jsonify({'status': 400, 'message': 'Quá thời hạn 2 tuần để hủy môn!'})

        phieu_dang_ky = dao.get_dang_ky_by_id(id)

        if not phieu_dang_ky:
            return jsonify({'status': 404, 'message': 'Không tìm thấy dữ liệu đăng ký này!'})

        # Chỉ sinh viên đăng ký mới được huỷ
        if phieu_dang_ky.sinh_vien_id != current_user.id:
            return jsonify({'status': 403, 'message': 'Không có quyền hủy!'})

        danh_sach_da_dang_ky = dao.get_registered_classes(phieu_dang_ky.sinh_vien_id)

        tong_tc_hien_tai = sum(ds.lop_hoc_phan.mon_hoc.so_tin_chi for ds in danh_sach_da_dang_ky)
        so_tin_chi_mon_xoa = phieu_dang_ky.lop_hoc_phan.mon_hoc.so_tin_chi

        if (tong_tc_hien_tai - so_tin_chi_mon_xoa) < TIN_CHI_TOI_THIEU:
            return jsonify({
                'status': 400,
                'message': f'Quy định tối thiểu {TIN_CHI_TOI_THIEU} TC. Hiện tại bạn có {tong_tc_hien_tai} TC, xóa môn này sẽ không đủ điều kiện.'
            })

        # Kiểm tra đã thi giữa kỳ chưa
        if phieu_dang_ky.lop_hoc_phan.da_thi_giua_ky:
            return jsonify({'status': 400, 'message': 'Môn đã có điểm giữa kỳ, không thể hủy!'})

        db.session.delete(phieu_dang_ky)
        db.session.commit()
        return jsonify({'status': 200, 'message': 'Hủy môn thành công!'})

    @app.route("/class_register")
    @login_required
    def class_register():
        cart = session.get('cart', {})
        lop_cho = list(cart.values())
        tong_tc = sum(int(item['tin_chi']) for item in lop_cho)

        danh_sach_mon_da_dang_ky = dao.get_registered_classes(current_user.id)

        for mon in danh_sach_mon_da_dang_ky:
            tong_tc += mon.lop_hoc_phan.mon_hoc.so_tin_chi



        # rang buoc huy mon sau 2 tuan hoc
        huy_mon_da_dang_ky = True
        if datetime.now() > HAN_HUY_MON:
            huy_mon_da_dang_ky = False
        
        # het han dang ky mon
        huy_mon_ghi_danh = True
        if datetime.now() > HAN_DANG_KY:
            huy_mon_ghi_danh = False

        return render_template('class_register.html',
                               lop_cho=lop_cho,
                               tong_tc=tong_tc,
                               history=danh_sach_mon_da_dang_ky,
                               huy_mon_da_dang_ky=huy_mon_da_dang_ky,
                               huy_mon_ghi_danh=huy_mon_ghi_danh,
                               HAN_DANG_KY=HAN_DANG_KY,
                               TIN_CHI_TOI_THIEU=TIN_CHI_TOI_THIEU)

    @app.route('/timetable')
    @login_required
    def timetable():
        ds_dang_ky = dao.get_registered_classes(current_user.id)
        lop_da_xac_nhan = [ds.lop_hoc_phan for ds in ds_dang_ky]
        return render_template('timetable.html', lop_da_xac_nhan=lop_da_xac_nhan)

    @app.route('/api/checkout', methods=['POST'])
    @login_required
    def checkout():
        cart = session.get('cart', {})
        if not cart:
            return jsonify({'status': 400, 'message': 'Danh sách đang trống!'})

        lop_cho = list(cart.values())
        tong_tc = sum(int(item['tin_chi']) for item in lop_cho)

        danh_sach_mon_da_dang_ky = dao.get_registered_classes(current_user.id)
        for mon in danh_sach_mon_da_dang_ky:
            tong_tc += mon.lop_hoc_phan.mon_hoc.so_tin_chi

        if tong_tc < TIN_CHI_TOI_THIEU:
            return jsonify({'status': 400, 'message': 'Bạn chưa chọn đủ 12 tín chỉ!'})
        if tong_tc > TIN_CHI_TOI_DA:
            return jsonify({'status': 400, 'message': 'Bạn chọn quá 25 tín chỉ!'})

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
    return render_template("user_information.html")


@app.context_processor
def common_data():
    if current_user.is_authenticated:
        registered_ids = [ds.lop_hoc_phan_id for ds in current_user.ds_dang_ky]
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
