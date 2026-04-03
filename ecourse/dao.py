from sqlalchemy.exc import IntegrityError
from ecourse.models import User, HocKy, MonHoc, LopHocPhan, DangKy
from ecourse import db
from flask import current_app
import hashlib
from flask_login import current_user


def load_hoc_ky():
    return HocKy.query.filter(HocKy.active == True).all()

def load_lop_hoc_phan(hk_id = None, kw = None, page = None):
    query = LopHocPhan.query.filter(LopHocPhan.active == True)

    if hk_id:
        query = query.filter(LopHocPhan.hoc_ky_id.__eq__(hk_id))

    if kw:
        query =query.join(MonHoc).filter(MonHoc.name.contains(kw))

    if page:
        size = current_app.config["PAGE_SIZE"]
        start = (int(page)-1) *size
        query = query.slice(start,start+size)



    return query.all()

def count_lop_hoc_phan(hk_id = None, kw = None):
    query = LopHocPhan.query.filter(LopHocPhan.active == True)

    if hk_id:
        query=query.filter(LopHocPhan.hoc_ky_id.__eq__(hk_id))
    if kw:
        query =query.join(MonHoc).filter(MonHoc.name.contains(kw))

    return query.count()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password)).first()

def dang_ky_lop(lop_hoc_phan_id):
    if not current_user.is_authenticated:
        raise Exception("Chức năng cần đăng nhập để thực hiện")

    lop = LopHocPhan.query.get(lop_hoc_phan_id)
    if not lop:
        raise ValueError("Lớp học phần không tồn tại!")


    phieu_cu = DangKy.query.filter_by(
        sinh_vien_id = current_user.id,
        lop_hoc_phan_id = lop_hoc_phan_id
    ).first()

    if phieu_cu:
        raise Exception("Bạn đã đăng ký lớp học phần này rồi")

    so_luong_hien_tai = DangKy.query.filter(DangKy.lop_hoc_phan_id == lop_hoc_phan_id).count()
    if so_luong_hien_tai >= lop.so_luong_max:
        raise ValueError("Lớp học phần này đã đủ sĩ số")


    mon_hoc = MonHoc.query.get(lop.mon_hoc_id)
    if mon_hoc.mon_tien_quyet_id:
        da_qua_mon = DangKy.query.join(LopHocPhan).filter(
            DangKy.sinh_vien_id == current_user.id,
            LopHocPhan.mon_hoc_id == mon_hoc.mon_tien_quyet_id,
            DangKy.diem_tong_ket >= 5.0
        ).first()

        if not da_qua_mon:
            raise ValueError(f"Bạn chưa học môn tiên quyết: {mon_hoc.mon_tien_quyet.name}")

    phieu_dang_ky = DangKy(sinh_vien_id = current_user.id, lop_hoc_phan_id = lop.id)
    db.session.add(phieu_dang_ky)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise  e
