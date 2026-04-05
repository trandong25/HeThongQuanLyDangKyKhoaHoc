import cloudinary.uploader
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import redirect

from ecourse import app, dao, login_manager, db
from flask import render_template, request

from ecourse.models import MonHoc, User


@app.route("/")
def index():
    classes = dao.get_classes()
    return render_template("index.html", classes=classes)

@app.route("/login",methods=["GET","POST"])
def login():
    error_msg = None
    if request.method.__eq__("POST"):
        username = request.form.get("username")
        password = request.form.get("password")
        user = dao.auth_user(username,password)

        if user:
            login_user(user)
            next = request.args.get("next")
            return redirect(next if next else "/")
        else:
            error_msg = "Login Unsuccessful. Please check username and password"

    return render_template("login.html",error_msg=error_msg)

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id=user_id)

@app.route("/register",methods=["GET","POST"])
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

            if avatar:
                res = cloudinary.uploader.upload(avatar)
                file_path = res['secure_url']

            try:
                dao.add_user(name, username, password, avatar=file_path)
                return redirect('/login')
            except:
                db.session.rollback()
                error_msg = "Hệ thống đang bị lỗi! Vui lòng quay lại sau!"
        else:
            error_msg = "Mật khẩu không khớp!"

    return render_template("register.html", error_msg=error_msg)

@app.route("/history")
@login_required
def history():
    history_data = dao.get_registered_classes(current_user.id)
    return render_template("history.html", history = history_data)

if __name__== "__main__":
    with app.app_context():
        app.run(debug=True)