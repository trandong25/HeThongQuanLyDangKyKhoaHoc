from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime, Enum, Date
from sqlalchemy.orm import relationship
from datetime import datetime,date
from ecourse import db, app
from enum import Enum as UserEnum


class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, default=True)

class UserRole(UserEnum):
    SINHVIEN = 1
    ADMIN = 2

class User(BaseModel,UserMixin):
    name = Column(String(50), nullable=False)
    avatar = Column(String(100), default='https://res.cloudinary.com/dypvhnpqn/image/upload/v1774616172/download_wrwwzp.jpg')
    username = Column(String(50), nullable = False, unique = True)
    password = Column(String(50), nullable=False)
    user_role = Column(Enum(UserRole), default=UserRole.SINHVIEN)

    # 1 Sinh viên có nhiều lượt đăng ký
    ds_dang_ky = relationship('DangKy', backref='sinh_vien', lazy=True)

    def __str__(self):
        return self.name

class MonHoc(BaseModel):
    name = Column(String(100), nullable=False)
    so_tin_chi = Column(Integer, nullable=False)

    mon_tien_quyet_id = Column(Integer,ForeignKey('mon_hoc.id'), nullable=True)
    #khi cần lấy môn tiên quyết mh.mon_tien_quyet.name
    # remote_side chỉ đích đến
    mon_tien_quyet = relationship('MonHoc', remote_side='MonHoc.id')


    ds_lop_hoc_phan = relationship('LopHocPhan', backref='mon_hoc', lazy= True)

    def __str__(self):
        return self.name

class HocKy(BaseModel):
    name = Column(String(50), nullable=False)
    ngay_bat_dau = Column(Date,nullable=False)
    han_dang_ky = Column(DateTime, nullable=False)

    ds_lop_hoc_phan = relationship('LopHocPhan', backref='hoc_ky', lazy=True)

    def __str__(self):
        return self.name

class LopHocPhan(BaseModel):
    mon_hoc_id = Column(Integer, ForeignKey(MonHoc.id), nullable=False)
    hoc_ky_id = Column(Integer,ForeignKey(HocKy.id),nullable=False)

    phong_hoc = Column(String(20),nullable=False)
    thu = Column(Integer, nullable=False)
    ca_hoc = Column(Integer, nullable=False)
    so_luong_max = Column(Integer, default=50)
    da_thi_giua_ky = Column(Boolean, default=False)

    ds_dang_ky = relationship('DangKy', backref='lop_hoc_phan', lazy=True)

class DangKy(BaseModel):
    sinh_vien_id = Column(Integer, ForeignKey(User.id), nullable=False)
    lop_hoc_phan_id = Column(Integer, ForeignKey(LopHocPhan.id), nullable=False)
    ngay_dang_ky = Column(DateTime, default=datetime.now())

    # dùng cho ràng buộc không đăng ký môn đã học
    diem_tong_ket = Column(Float, nullable=True)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # 1. Tạo Môn Học mẫu
        mh1 = MonHoc(name="Lập trình Python", so_tin_chi=3)
        mh2 = MonHoc(name="Cấu trúc dữ liệu", so_tin_chi=4)

        # 2. Tạo Học Kỳ mẫu
        hk1 = HocKy(name="Học kỳ 1 - 2026", ngay_bat_dau=date(2026, 9, 5), han_dang_ky=datetime(2026, 9, 20, 23, 59))

        # Đẩy Môn học và Học kỳ vào DB trước để lấy ID
        db.session.add_all([mh1, mh2, hk1])
        db.session.commit()

        # 3. Tạo Lớp Học Phần mẫu (Liên kết với Môn học và Học kỳ ở trên)
        lhp1 = LopHocPhan(mon_hoc_id=mh1.id, hoc_ky_id=hk1.id, phong_hoc="Phòng A101", thu=2, ca_hoc=1, so_luong_max=40)
        lhp2 = LopHocPhan(mon_hoc_id=mh2.id, hoc_ky_id=hk1.id, phong_hoc="Phòng B205", thu=4, ca_hoc=3, so_luong_max=50)

        db.session.add_all([lhp1, lhp2])
        db.session.commit()

        print("Đã chạy xong dữ liệu giả !")