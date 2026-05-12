from sqlalchemy.exc import IntegrityError
from ecourse.models import User, HocKy, MonHoc, LopHocPhan, DangKy
from ecourse import db
from flask import current_app
import hashlib
from flask_login import current_user
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import joinedload

def load_courses():
    return MonHoc.query.all()

def load_hoc_ky():
    return HocKy.query.filter(HocKy.active == True).all()

def load_lop_hoc_phan(hk_id = None, kw = None, page = None):
    query = LopHocPhan.query.join(HocKy).filter(LopHocPhan.active == True, HocKy.active == True)
    if hk_id:
        query = query.filter(LopHocPhan.hoc_ky_id == hk_id)

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
        query=query.filter(LopHocPhan.hoc_ky_id == hk_id)
    if kw:
        query =query.join(MonHoc).filter(MonHoc.name.contains(kw))

    return query.count()

def get_lop_hoc_phan_by_id(lop_phan_id):
    return LopHocPhan.query.get(lop_phan_id)
def get_hoc_ky_by_id(hoc_ky_id):
    return HocKy.query.get(hoc_ky_id)
def get_dang_ky_by_id(hoc_ky_id):
    return DangKy.query.get(hoc_ky_id)


def get_user_by_id(user_id):
    return User.query.get(user_id)
def get_user_by_username(username):
    return User.query.filter(User.username == username).first()

def dang_ky_lop(lop_hoc_phan_id):
    #Ràng buộc cho sinh viên phải đăng nhập để đăng ký
    if not current_user.is_authenticated:
        raise Exception("Chức năng cần đăng nhập để thực hiện")

    # Ràng buộc cho lớp tồn tại
    lop = LopHocPhan.query.get(lop_hoc_phan_id)
    if not lop:
        raise ValueError("Lớp học phần không tồn tại!")

    if not lop.active:
        raise ValueError("Lớp học phần này đang bị khóa hoặc chưa mở")

    #Ràng buộc cho không được đăng ký sau thời hạn và học kỳ chưa active
    hoc_ky = HocKy.query.get(lop.hoc_ky_id)

    if not hoc_ky.active:
        raise ValueError("Học kỳ chứa môn hiện không trong thời gian đăng ký")
    if datetime.now() > hoc_ky.han_dang_ky:
        raise ValueError("Đã hết thời hạn đăng ký")


    #Ràng buộc cho không được bấm đăng ký nhiều lần spam
    phieu_cu = DangKy.query.filter_by(
        sinh_vien_id = current_user.id,
        lop_hoc_phan_id = lop_hoc_phan_id
    ).first()
    if phieu_cu:
        raise Exception("Bạn đã đăng ký lớp học phần này rồi")

    #Ràng buộc cho không được đăng ký quá số lượng
    so_luong_hien_tai = DangKy.query.filter(DangKy.lop_hoc_phan_id == lop_hoc_phan_id).count()
    if so_luong_hien_tai >= lop.so_luong_max:
        raise ValueError("Lớp học phần này đã đủ sĩ số")

    mon_hoc = MonHoc.query.get(lop.mon_hoc_id)

    #Ràng buộc cho sinh viên không được đăng ký môn đã học rồi
    mon_da_hoc = DangKy.query.join(LopHocPhan).filter(
        DangKy.sinh_vien_id == current_user.id,
        LopHocPhan.mon_hoc_id == mon_hoc.id,
        DangKy.diem_tong_ket >=5
    ).first()
    if mon_da_hoc:
        raise ValueError("Bạn đã học và thi đạt môn này rồi")

    cac_phieu_dk = DangKy.query.join(LopHocPhan).options(
        joinedload(DangKy.lop_hoc_phan).joinedload(LopHocPhan.mon_hoc)
    ).filter(
        DangKy.sinh_vien_id == current_user.id,
        LopHocPhan.hoc_ky_id == lop.hoc_ky_id
    ).all()

    tong_tin_chi = mon_hoc.so_tin_chi

    for phieu in cac_phieu_dk:
        lhp_da_dk = phieu.lop_hoc_phan
        mh_da_dk = lhp_da_dk.mon_hoc

        if mh_da_dk.id == mon_hoc.id:
            raise ValueError(f"Bạn đã đăng ký lớp {lhp_da_dk.id} của môn {mh_da_dk.name} trong học kỳ này rồi!")

        #Ràng buộc không được đăng ký trùng lịch học cùng thứ, cùng ca
        if lhp_da_dk.thu == lop.thu and lhp_da_dk.ca_hoc == lop.ca_hoc:
            raise ValueError(f"Trùng lịch học với lớp {mh_da_dk.name} (Thứ {lhp_da_dk.thu}, Ca {lhp_da_dk.ca_hoc})")

        tong_tin_chi += mh_da_dk.so_tin_chi
    # Ràng buộc cho không được đăng ký quá 25tc
    if tong_tin_chi > 25:
        raise ValueError("Bạn đã vượt quá 25 tín chỉ")

    #Ràng buộc cho không được đăng ký nếu chưa học môn tiên quyết
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

    db.session.flush()



def get_registered_classes(user_id):
    return DangKy.query.filter(DangKy.sinh_vien_id == user_id).all()

def auth_user(username,password):
    password = hashlib.md5(password.encode("utf-8")).hexdigest()
    return User.query.filter(User.username == username, User.password == password).first()

def add_user(name,username,password,avatar):
    password = hashlib.md5(password.encode("utf-8")).hexdigest()
    u = User(name=name, username=username.strip(), password=password,avatar=avatar)
    db.session.add(u)
    db.session.commit()
    return u


def count_lop_by_mon_hoc():
    return db.session.query(MonHoc.id, MonHoc.name, func.count(LopHocPhan.id)
    ).join(LopHocPhan, LopHocPhan.mon_hoc_id == MonHoc.id,isouter=True
    ).group_by(MonHoc.id, MonHoc.name).all()


def count_sv_by_lop():
    return (db.session.query(LopHocPhan.id, MonHoc.name,func.count(DangKy.sinh_vien_id)).join(MonHoc, MonHoc.id == LopHocPhan.mon_hoc_id)
            .join(DangKy, DangKy.lop_hoc_phan_id == LopHocPhan.id, isouter=True)
            .group_by(LopHocPhan.id, MonHoc.name).all())