from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime, Enum, Date
from sqlalchemy.orm import relationship
from datetime import datetime
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

        import hashlib
        from datetime import datetime, timedelta

        default_password = str(hashlib.md5('123456'.encode('utf-8')).hexdigest())

        # 2. Tạo Users (1 Admin, 2 Sinh viên)
        admin = User(name='Giáo vụ Đào tạo', username='admin', password=default_password, active=True)
        sv1 = User(name='Nguyễn Sinh Viên 1', username='sv01', password=default_password, active=True)
        sv2 = User(name='Trần Sinh Viên 2', username='sv02', password=default_password, active=True)

        db.session.add_all([admin, sv1, sv2])
        db.session.commit()

        # 3 Tạo Học kỳ
        now = datetime.now()
        hk1 = HocKy(name="HK1 - 2026", active=True, ngay_bat_dau=now, han_dang_ky=now + timedelta(days=30))
        hk2 = HocKy(name="HK2 - 2026", active=False, ngay_bat_dau=now + timedelta(days=150),
                    han_dang_ky=now + timedelta(days=180))

        db.session.add_all([hk1, hk2])
        db.session.commit()

        # 4. Tạo Môn học
        m1 = MonHoc(name="Nhập môn Lập trình", so_tin_chi=3)
        m2 = MonHoc(name="Toán rời rạc", so_tin_chi=3)
        db.session.add_all([m1, m2])
        db.session.commit()

        m3 = MonHoc(name="Cấu trúc dữ liệu", so_tin_chi=3, mon_tien_quyet_id=m1.id)
        m4 = MonHoc(name="Cơ sở dữ liệu", so_tin_chi=3)
        db.session.add_all([m3, m4])
        db.session.commit()

        # 5. Tạo Lớp học phần
        l1 = LopHocPhan(mon_hoc_id=m1.id, hoc_ky_id=hk1.id, so_luong_max=50,
                        active=True, phong_hoc="A101", thu=2,ca_hoc=1)
        l2 = LopHocPhan(mon_hoc_id=m2.id, hoc_ky_id=hk1.id, so_luong_max=50,
                        active=True, phong_hoc="B202", thu=3,ca_hoc=2)
        l3 = LopHocPhan(mon_hoc_id=m3.id, hoc_ky_id=hk1.id, so_luong_max=40,
                        active=True, phong_hoc="C303", thu=4,ca_hoc=1)
        l4 = LopHocPhan(mon_hoc_id=m4.id, hoc_ky_id=hk1.id, so_luong_max=1,
                        active=True, phong_hoc="D404", thu=5,ca_hoc=3)

        db.session.add_all([l1, l2, l3, l4])
        db.session.commit()
