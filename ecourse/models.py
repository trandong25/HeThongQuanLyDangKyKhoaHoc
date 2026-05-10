from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime, Enum, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
from ecourse import db, app
from enum import Enum as UserEnum
import hashlib, random


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

    # 1 sinh viên có nhiều lượt đăng ký
    ds_dang_ky = relationship('DangKy', backref='sinh_vien', lazy=True)

    def __str__(self):
        return self.name

class MonHoc(BaseModel):
    name = Column(String(100), nullable=False)
    so_tin_chi = Column(Integer, nullable=False)

    mon_tien_quyet_id = Column(Integer,ForeignKey('mon_hoc.id'), nullable=True)

    # remote_side chỉ đích đến
    mon_tien_quyet = relationship('MonHoc', remote_side='MonHoc.id')


    ds_lop_hoc_phan = relationship('LopHocPhan', back_populates='mon_hoc', lazy= True)

    def __str__(self):
        return self.name

class HocKy(BaseModel):
    name = Column(String(50), nullable=False)
    ngay_bat_dau = Column(Date,nullable=False)
    han_dang_ky = Column(DateTime, nullable=False)

    ds_lop_hoc_phan = relationship('LopHocPhan', back_populates='hoc_ky', lazy=True)

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

    mon_hoc= relationship('MonHoc', back_populates='ds_lop_hoc_phan')
    hoc_ky= relationship('HocKy', back_populates='ds_lop_hoc_phan')

    ds_dang_ky = relationship('DangKy', backref='lop_hoc_phan', lazy=True)

class DangKy(BaseModel):
    sinh_vien_id = Column(Integer, ForeignKey(User.id), nullable=False)
    lop_hoc_phan_id = Column(Integer, ForeignKey(LopHocPhan.id), nullable=False)
    ngay_dang_ky = Column(DateTime, default=datetime.now())

    # dùng cho ràng buộc không đăng ký môn đã học
    diem_tong_ket = Column(Float, nullable=True)


if __name__ == '__main__':
    with app.app_context():
        # 1. Xóa toàn bộ dữ liệu cũ và tạo bảng mới
        db.drop_all()
        db.create_all()


        # 2. Tạo user và admin
        user1 = User(
            name="Nguyễn Văn Sinh Viên",
            username="student1",
            password=hashlib.md5("123456".encode('utf-8')).hexdigest(),
            user_role=UserRole.SINHVIEN
        )
        admin1 = User(
            name="Quản Trị Viên",
            username="admin",
            password=hashlib.md5("123456".encode('utf-8')).hexdigest(),
            user_role=UserRole.ADMIN
        )
        db.session.add_all([user1, admin1])
        db.session.commit()

        # 3. Tạo học kì
        hk1 = HocKy(name="Học kỳ 1 - 2026", ngay_bat_dau=date(2026, 9, 5), han_dang_ky=datetime(2026, 9, 20, 23, 59))
        db.session.add(hk1)
        db.session.commit()

        # 4. Danh sách các môn
        danh_sach_ten_mon = [
            "Lập trình Python", "Cấu trúc dữ liệu", "Trí tuệ nhân tạo", "Cơ sở dữ liệu",
            "Mạng máy tính", "Hệ điều hành", "Toán rời rạc", "Giải tích 1", "Giải tích 2",
            "Vật lý 1", "Vật lý 2", "Triết học Mác-Lênin", "Kỹ năng mềm", "Tiếng Anh 1",
            "Tiếng Anh 2", "Phát triển Web", "Phát triển Mobile", "Kiến trúc máy tính",
            "An toàn thông tin", "Khai phá dữ liệu", "Học máy", "Đồ họa máy tính",
            "Thiết kế UI/UX", "Kiểm thử phần mềm", "Quản trị dự án CNTT", "Thương mại điện tử",
            "Điện toán đám mây", "Lập trình Java", "Phân tích thiết kế hệ thống", "Xác suất thống kê"
        ]

        danh_sach_phong = ["A101", "A102", "A205", "B104", "B201", "C302", "C405", "D101", "D202"]

        # 5. Tạo môn học và lớp học phần
        for i, ten_mon in enumerate(danh_sach_ten_mon):
            mh = MonHoc(name=ten_mon, so_tin_chi=random.randint(2, 4))
            db.session.add(mh)
            db.session.commit()

            # TẠO NHIỀU LỚP HỌC PHẦN (Lịch khác nhau) cho 5 MÔN ĐẦU TIÊN để dễ test
            # Các môn còn lại chỉ tạo 1 lớp
            so_luong_lop = 3 if i < 5 else 1
            lich_da_tao = set()  # Dùng set để lưu lịch, tránh tạo 2 lớp cùng 1 môn bị trùng lịch nhau

            for _ in range(so_luong_lop):
                while True:
                    thu = random.randint(2, 7)
                    ca_hoc = random.randint(1, 4)
                    if (thu, ca_hoc) not in lich_da_tao:
                        lich_da_tao.add((thu, ca_hoc))
                        break

                lhp = LopHocPhan(
                    mon_hoc_id=mh.id,
                    hoc_ky_id=hk1.id,
                    phong_hoc=random.choice(danh_sach_phong),
                    thu=thu,
                    ca_hoc=ca_hoc,
                    so_luong_max=random.choice([30, 40, 50])
                )
                db.session.add(lhp)

        db.session.commit()

