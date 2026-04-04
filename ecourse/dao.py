import hashlib

from ecourse import db
from ecourse.models import MonHoc,User,LopHocPhan,DangKy

def load_courses():
    return MonHoc.query.all()

def get_classes():
    return LopHocPhan.query.all()

def get_registered_classes(user_id):
    return DangKy.query.filter(DangKy.sinh_vien_id == user_id).all()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def auth_user(username,password):
    password = hashlib.md5(password.encode("utf-8")).hexdigest()
    return User.query.filter(User.username == username, User.password == password).first()

def add_user(name,username,password,avatar):
    password = hashlib.md5(password.encode("utf-8")).hexdigest()
    u = User(name=name, username=username.strip(), password=password,avatar=avatar)
    db.session.add(u)
    db.session.commit()
    return u