from ecourse import app,dao
from flask_login import login_required
from flask import request, jsonify


@app.route("/")
def index():
    return "Hello world, Đây là Hệ thống Quản lý Đăng ký Khóa học!"

@app.route('/api/dang-ky', methods= ['post'])
@login_required
def api_dang_ky_lop():
    try:
        data= request.json
        lop_id = data.get('lop_hoc_phan_id')

        if not lop_id:
            return jsonify({'status': 400, 'err_msg':'Thiếu mã lớp học phần'})

        dao.dang_ky_lop(lop_id)

        return jsonify({
            'status': 200,
            'message': 'Đăng ký học phần thành công'
        })

    except ValueError as ex:
        return jsonify({'status': 400, 'err_msg': str(ex)})


    except Exception as ex:
        return jsonify({'status': 400, 'err_msg': str(ex)})


if __name__== "__main__":
    with app.app_context():
        app.run(debug=True, port=5000)