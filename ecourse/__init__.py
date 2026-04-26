from datetime import datetime

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
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:abcd@localhost/course_db?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

app.config["PAGE_SIZE"] = 10

db = SQLAlchemy(app)

login_manager = LoginManager(app)

NGAY_BAT_DAU_DANG_KY = datetime(2026,4,1,12,0,0)

NGAY_BAT_DAU_HK = datetime(2026, 4, 16,0,0,0)
TIN_CHI_TOI_THIEU = 12
TIN_CHI_TOI_DA = 25
