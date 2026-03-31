from ecourse import app
from flask import render_template

from ecourse.models import MonHoc


@app.route("/")
def index():
    courses = MonHoc.query.all()
    return render_template("index.html", courses=courses)


if __name__== "__main__":
    with app.app_context():
        app.run(debug=True)