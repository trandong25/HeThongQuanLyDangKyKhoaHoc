import math

import cloudinary.uploader
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import redirect
from ecourse import app, dao, login_manager, db
from flask import render_template, request, session
from ecourse.models import MonHoc, User, LopHocPhan, DangKy
from ecourse import app,dao
from flask_login import login_required
from flask import request, jsonify


def register_route(app):
    @app.route("/")
    def index():
        page = request.args.get("page",1,type=int)

        kw = request.args.get("kw")
        pages = math.ceil(dao.count_lop_hoc_phan()/app.config['PAGE_SIZE'])
        classes = dao.load_lop_hoc_phan(kw=kw,page=page)
        return render_template("index.html", classes=classes,pages = pages,curent_page=page)

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
                error_msg = "Login Unsuccessful. Please check username and password"

        return render_template("login.html", error_msg=error_msg)

    @app.route("/logout")
    def logout():
        logout_user()
        return redirect("/")

    @app.route('/api/dang-ky', methods=['post'])
    @login_required
    def api_dang_ky_lop():
        try:
            data = request.json
            lop_id = data.get('lop_hoc_phan_id')

            if not lop_id:
                return jsonify({'status': 400, 'err_msg': 'Thiếu mã lớp học phần'})

            dao.dang_ky_lop(lop_id)

            return jsonify({
                'status': 200,
                'message': 'Đăng ký học phần thành công'
            })

        except ValueError as ex:
            return jsonify({'status': 400, 'err_msg': str(ex)})


        except Exception as ex:
            return jsonify({'status': 400, 'err_msg': str(ex)})

    @app.route('/api/dang_ky_tam', methods=['POST'])
    @login_required
    def api_dang_ky_tam():
        cart = session.get('cart', {})
        data = request.json

        new_id = str(data.get('id'))
        new_name = data.get('name')
        new_thu = str(data.get('thu'))
        new_ca = str(data.get('ca_hoc'))


        if new_id in cart:
            return jsonify({'status': 400, 'err_msg': 'Môn này đã có trong giỏ hàng!'})


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
                    'err_msg': f'Trùng lịch! Thứ {new_thu} - Ca {new_ca} bạn đã có Lịch học môn {lop_da_dk.mon_hoc.name}.'
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
            del cart[id]  # Xóa khỏi Giỏ hàng
            session['cart'] = cart
            return jsonify({'status': 200, 'message': 'Đã xóa thành công'})
        return jsonify({'status': 400, 'err_msg': 'Môn học không tồn tại trong giỏ'})

    @app.route("/class_register")
    @login_required
    def class_register():
        cart = session.get('cart',{})
        lop_cho = list(cart.values()) if cart else []
        tong_tc = sum(int(item['tin_chi']) for item in lop_cho)
        history_data = dao.get_registered_classes(current_user.id)
        return render_template('class_register.html',lop_cho=lop_cho, tong_tc=tong_tc,history=history_data)

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
            return jsonify({'status': 400, 'message': 'Giỏ hàng đang trống!'})
        lop_cho = list(cart.values())
        tong_tc = sum(int(item['tin_chi']) for item in lop_cho)
        if tong_tc < 12:
            return jsonify({'status': 400, 'message': 'Bạn chưa chọn đủ 12 tín chỉ!'})
        try:
            for item in lop_cho:
                lop_id = int(item['id'])
                exist = DangKy.query.filter_by(sinh_vien_id=current_user.id, lop_hoc_phan_id=lop_id).first()
                if not exist:
                    dk = DangKy(sinh_vien_id=current_user.id, lop_hoc_phan_id=lop_id)
                    db.session.add(dk)
            db.session.commit()
            session.pop('cart', None)  # Xóa giỏ hàng
            return jsonify({'status': 200, 'message': 'Xác nhận nhập học thành công!'})
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
            registered_ids = [dk.lop_hoc_phan_id  for dk in current_user.ds_dang_ky]
        else:
            registered_ids = []

        return dict(registered_ids=registered_ids)

@login_manager.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id=user_id)


if __name__== "__main__":
    register_route(app=app)
    app.run(debug=True)