import cloudinary
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

cloudinary.config(
    cloud_name = "dz46tygsf",
    api_key = "399971149668821",
    api_secret = "SeXVDWlex0ppidZyCrMSoinwiYY"
)
app = Flask(__name__)

app.secret_key = "asjdahjsdaskdjahsd%#adsd"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:123456@localhost/course_db?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

app.config["PAGE_SIZE"] = 10

db = SQLAlchemy(app)

login_manager = LoginManager(app)