from ecourse import app, db
from ecourse.models import User, UserRole, HocKy, MonHoc, LopHocPhan, DangKy
import hashlib
from datetime import datetime, date, timedelta


def create_full_mock_data():
    with app.app_context():
        # 1. LÀM SẠCH DATABASE
        db.drop_all()
        db.create_all()
        print("Đang dọn dẹp và xây lại Database...")

        # ==========================================
        # 2. TẠO USER (ADMIN & SINH VIÊN)
        # ==========================================
        pw = hashlib.md5('123456'.encode('utf-8')).hexdigest()
        admin = User(name="Quản Trị Viên", username="admin", password=pw, user_role=UserRole.ADMIN)
        sv_test = User(name="Sinh Viên Test", username="svtest", password=pw, user_role=UserRole.SINHVIEN)
        sv_clone = User(name="Kẻ Giữ Chỗ", username="kegiucho", password=pw, user_role=UserRole.SINHVIEN)
        db.session.add_all([admin, sv_test, sv_clone])
        db.session.commit()

        # ==========================================
        # 3. TẠO CÁC HỌC KỲ (BẪY THỜI GIAN)
        # ==========================================
        # HK Quá Khứ (Để test môn đã học)
        hk_past = HocKy(name="HK Trước (Đã qua)", ngay_bat_dau=date(2025, 1, 1), han_dang_ky=datetime(2025, 1, 15),
                        active=False)

        # HK Hiện Tại (Chuẩn để đăng ký) - Bắt đầu tuần sau
        hk_current = HocKy(name="HK Hiện Tại (Đang mở)", ngay_bat_dau=date.today() + timedelta(days=7),
                           han_dang_ky=datetime.now() + timedelta(days=15), active=True)

        # HK Hết Hạn Đăng Ký (Bẫy: Hạn ĐK đã qua)
        hk_late = HocKy(name="HK Đã Đóng Cổng", ngay_bat_dau=date.today() + timedelta(days=7),
                        han_dang_ky=datetime.now() - timedelta(days=1), active=True)

        # HK Đã Học 3 Tuần (Bẫy: Cấm hủy môn sau 2 tuần)
        hk_started = HocKy(name="HK Đã Học 3 Tuần", ngay_bat_dau=date.today() - timedelta(days=21),
                           han_dang_ky=datetime.now() + timedelta(days=30), active=True)

        db.session.add_all([hk_past, hk_current, hk_late, hk_started])
        db.session.commit()

        # ==========================================
        # 4. TẠO MÔN HỌC (BẪY TIÊN QUYẾT & TÍN CHỈ)
        # ==========================================
        mh_ly = MonHoc(name="Vật lý 1", so_tin_chi=3)  # Môn dùng để test "Đã qua môn"
        mh_c = MonHoc(name="Lập trình C", so_tin_chi=3)  # Môn gốc
        db.session.add_all([mh_ly, mh_c])
        db.session.commit()

        mh_ctdl = MonHoc(name="Cấu trúc dữ liệu", so_tin_chi=3, mon_tien_quyet_id=mh_c.id)  # Bẫy Tiên quyết
        mh_ai = MonHoc(name="Trí tuệ nhân tạo", so_tin_chi=4)  # Bẫy Sĩ số
        mh_toan = MonHoc(name="Toán rời rạc", so_tin_chi=4)  # Bẫy Trùng lịch

        # Nhóm môn nhồi tín chỉ (Để test max 25 TC)
        mh_csdl = MonHoc(name="Cơ sở dữ liệu", so_tin_chi=4)
        mh_mang = MonHoc(name="Mạng máy tính", so_tin_chi=4)
        mh_hdt = MonHoc(name="Lập trình HĐT", so_tin_chi=4)
        mh_web = MonHoc(name="Phát triển Web", so_tin_chi=4)

        db.session.add_all([mh_ctdl, mh_ai, mh_toan, mh_csdl, mh_mang, mh_hdt, mh_web])
        db.session.commit()

        # ==========================================
        # 5. TẠO LỚP HỌC PHẦN (CÁC BẪY RÀNG BUỘC)
        # ==========================================
        # 5.1. Lớp của Học kỳ quá khứ (Test đã qua môn)
        lhp_ly_past = LopHocPhan(mon_hoc_id=mh_ly.id, hoc_ky_id=hk_past.id, phong_hoc="A100", thu=2, ca_hoc=1,
                                 so_luong_max=50)

        # 5.2. Lớp của HK Hết hạn (Test Hạn ĐK)
        lhp_tre_han = LopHocPhan(mon_hoc_id=mh_c.id, hoc_ky_id=hk_late.id, phong_hoc="A101", thu=3, ca_hoc=1,
                                 so_luong_max=50)

        # 5.3. Lớp của HK Đã học 3 tuần (Test cấm hủy sau 2 tuần)
        lhp_cam_huy_time = LopHocPhan(mon_hoc_id=mh_csdl.id, hoc_ky_id=hk_started.id, phong_hoc="A102", thu=4, ca_hoc=1,
                                      so_luong_max=50)

        # 5.4. Lớp của HK Hiện Tại (Các bẫy chính)
        lhp_c = LopHocPhan(mon_hoc_id=mh_c.id, hoc_ky_id=hk_current.id, phong_hoc="B201", thu=2, ca_hoc=1,
                           so_luong_max=50)
        lhp_toan = LopHocPhan(mon_hoc_id=mh_toan.id, hoc_ky_id=hk_current.id, phong_hoc="B202", thu=2, ca_hoc=1,
                              so_luong_max=50)  # Trùng lịch với lhp_c
        lhp_ctdl = LopHocPhan(mon_hoc_id=mh_ctdl.id, hoc_ky_id=hk_current.id, phong_hoc="B203", thu=3, ca_hoc=2,
                              so_luong_max=50)  # Tiên quyết C
        lhp_ai = LopHocPhan(mon_hoc_id=mh_ai.id, hoc_ky_id=hk_current.id, phong_hoc="B204", thu=4, ca_hoc=1,
                            so_luong_max=1)  # Bẫy Sĩ số (Max = 1)

        # Lớp bẫy thi giữa kỳ (Cấm hủy)
        lhp_thi_roi = LopHocPhan(mon_hoc_id=mh_mang.id, hoc_ky_id=hk_current.id, phong_hoc="C301", thu=5, ca_hoc=1,
                                 so_luong_max=50, da_thi_giua_ky=True)

        # Nhóm môn nhồi để test 12 - 25 TC
        lhp_ly_current = LopHocPhan(mon_hoc_id=mh_ly.id, hoc_ky_id=hk_current.id, phong_hoc="C302", thu=6, ca_hoc=1,
                                    so_luong_max=50)
        lhp_hdt = LopHocPhan(mon_hoc_id=mh_hdt.id, hoc_ky_id=hk_current.id, phong_hoc="D401", thu=6, ca_hoc=2,
                             so_luong_max=50)
        lhp_web = LopHocPhan(mon_hoc_id=mh_web.id, hoc_ky_id=hk_current.id, phong_hoc="D402", thu=7, ca_hoc=1,
                             so_luong_max=50)

        db.session.add_all(
            [lhp_ly_past, lhp_tre_han, lhp_cam_huy_time, lhp_c, lhp_toan, lhp_ctdl, lhp_ai, lhp_thi_roi, lhp_ly_current,
             lhp_hdt, lhp_web])
        db.session.commit()

        # ==========================================
        # 6. GÀI BẪY VÀO BẢNG ĐĂNG KÝ (DỮ LIỆU ĐÃ CÓ SẴN)
        # ==========================================
        # 6.1. svtest đã học và PASS môn Vật Lý 1 kỳ trước (Điểm 8.0)
        dk_qua_mon = DangKy(sinh_vien_id=sv_test.id, lop_hoc_phan_id=lhp_ly_past.id, diem_tong_ket=8.0,
                            ngay_dang_ky=datetime(2025, 1, 2))

        # 6.2. kegiucho đã đăng ký môn AI (Làm lớp AI bị Full 1/1)
        dk_full = DangKy(sinh_vien_id=sv_clone.id, lop_hoc_phan_id=lhp_ai.id)

        # 6.3. svtest đang đăng ký lớp "Cấm hủy do quá 2 tuần" và "Cấm hủy do đã thi giữa kỳ"
        dk_cam_huy_1 = DangKy(sinh_vien_id=sv_test.id, lop_hoc_phan_id=lhp_cam_huy_time.id)
        dk_cam_huy_2 = DangKy(sinh_vien_id=sv_test.id, lop_hoc_phan_id=lhp_thi_roi.id)

        db.session.add_all([dk_qua_mon, dk_full, dk_cam_huy_1, dk_cam_huy_2])
        db.session.commit()

        print("✅ ĐÃ TẠO XONG DỮ LIỆU TEST TOÀN DIỆN!")
        print("Tài khoản Sinh viên: username: svtest | pass: 123456")
        print("Tài khoản Admin: username: admin | pass: 123456")


if __name__ == '__main__':
    create_full_mock_data()