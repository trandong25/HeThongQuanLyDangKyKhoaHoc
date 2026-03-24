from ecourse import app

@app.route("/")
def index():
    return "Hello world, Đây là Hệ thống Quản lý Đăng ký Khóa học!"


if __name__== "__main__":
    with app.app_context():
        app.run(debug=True, port=5000)