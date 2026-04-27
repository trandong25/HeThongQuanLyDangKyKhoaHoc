import unittest,pytest
from datetime import datetime, timedelta
from ecourse.test.test_base import test_app,test_client, test_session
from ecourse.models import DangKy, MonHoc, LopHocPhan, HocKy, User
from datetime import datetime as real_datetime

@pytest.fixture
def sample_student(test_session):
    sv = User(name="Sinh Vien Test", username="sv_test_01", password="123", active=True)
    test_session.add(sv)
    test_session.commit()
    return sv

@pytest.fixture
def sample_lop_hoc_phan(test_session):
    ngay_hien_tai = datetime.now()
    fake_han_dang_ky = ngay_hien_tai + timedelta(days=30)
    hk1 = HocKy(name="HK1", active=True, ngay_bat_dau=ngay_hien_tai, han_dang_ky=fake_han_dang_ky)
    test_session.add(hk1)
    test_session.commit()

    m1 = MonHoc(name="Python cơ bản", so_tin_chi=3)
    m2 = MonHoc(name="Lập trình Python", so_tin_chi=3)
    test_session.add_all([m1, m2])
    test_session.commit()

    l1 = LopHocPhan(mon_hoc_id=m1.id, hoc_ky_id=hk1.id, so_luong_max=50, active=True, phong_hoc="A101", thu=2, ca_hoc=1)
    l2 = LopHocPhan(mon_hoc_id=m2.id, hoc_ky_id=hk1.id, so_luong_max=50, active=True, phong_hoc="B202", thu=3, ca_hoc=2)
    test_session.add_all([l1, l2])
    test_session.commit()

    return [l1, l2]

def test_huy_mon(test_client, test_session, sample_student, sample_lop_hoc_phan, mocker):
    # ===== 1. Fake user =====
    class FakeUser:
        is_authenticated = True
        id = sample_student.id

    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())
    mocker.patch("ecourse.index.current_user", new=FakeUser())

    l1, l2 = sample_lop_hoc_phan

    # ===== 2. Tạo dữ liệu đăng ký =====
    dk1 = DangKy(sinh_vien_id=sample_student.id, lop_hoc_phan_id=l1.id)
    dk2 = DangKy(sinh_vien_id=sample_student.id, lop_hoc_phan_id=l2.id)
    test_session.add_all([dk1, dk2])
    test_session.commit()

    # ===== 3. Setup tín chỉ =====
    MonHoc.query.get(l1.mon_hoc_id).so_tin_chi = 15
    MonHoc.query.get(l2.mon_hoc_id).so_tin_chi = 5
    test_session.commit()

    # ===== 4. Mock thời gian =====
    fake_now = real_datetime(2020, 1, 1)

    datetime_mock = mocker.patch("ecourse.index.datetime")
    datetime_mock.now.return_value = fake_now
    datetime_mock.side_effect = lambda *args, **kwargs: real_datetime(*args, **kwargs)

    # ===== 5. Gọi API =====
    response = test_client.delete(f"/api/xoa_mon_da_dang_ky/{dk2.id}")
    data = response.get_json()

    # ===== 6. Assert =====
    assert response.status_code == 200
    assert data["status"] == 200
    assert DangKy.query.count() == 1

def test_huy_mon_duoi_12_tin_chi(test_client, test_session, sample_student, sample_lop_hoc_phan, mocker):
    """Test chặn hủy môn nếu thao tác này làm sinh viên rớt xuống dưới 12 TC"""

    class FakeUser:
        is_authenticated = True
        id = sample_student.id

    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())
    mocker.patch("ecourse.index.current_user", new=FakeUser())

    l1 = sample_lop_hoc_phan[0]
    dk = DangKy(sinh_vien_id=sample_student.id, lop_hoc_phan_id=l1.id)
    test_session.add(dk)

    m1 = MonHoc.query.get(l1.mon_hoc_id)
    m1.so_tin_chi = 13  # Đang có 13 TC
    test_session.commit()

    # Xóa 1 phát là còn 0 TC (vi phạm < 12)
    response = test_client.delete(f"/api/xoa_mon_da_dang_ky/{dk.id}")
    data = response.get_json()

    assert response.status_code == 200  # HTTP Request thành công
    assert data["status"] == 400  # Nhưng Business Logic trả về lỗi 400
    assert DangKy.query.count() == 1  # Phiếu đăng ký vẫn còn nguyên trong DB, không bị xóa

def test_huy_mon_qua_han_2_tuan(test_client, test_session, sample_student, sample_lop_hoc_phan, mocker):
    """Test chặn hủy môn nếu đã lố 2 tuần kể từ ngày bắt đầu học kỳ"""

    class FakeUser:
        is_authenticated = True
        id = sample_student.id

    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())
    mocker.patch("ecourse.index.current_user", new=FakeUser())

    l1 = sample_lop_hoc_phan[0]
    dk = DangKy(sinh_vien_id=sample_student.id, lop_hoc_phan_id=l1.id)
    test_session.add(dk)
    test_session.commit()

    # Mock ngày hiện tại thành năm 2030 (để chắc chắn đã quá 2 tuần)
    fake_now = datetime(2030, 1, 1)
    datetime_mock = mocker.patch("ecourse.index.datetime")  # Chỉnh thành file chứa API của bạn
    datetime_mock.now.return_value = fake_now

    response = test_client.delete(f"/api/xoa_mon_da_dang_ky/{dk.id}")
    data = response.get_json()

    assert data["status"] == 400
    assert "Quá thời hạn" in data["message"]


def test_huy_mon_da_thi_giua_ky(test_client, test_session, sample_student, sample_lop_hoc_phan, mocker):
    class FakeUser:
        is_authenticated = True
        id = sample_student.id

    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())
    mocker.patch("ecourse.index.current_user", new=FakeUser())

    l1, l2 = sample_lop_hoc_phan[0], sample_lop_hoc_phan[1]

    m1 = MonHoc.query.get(l1.mon_hoc_id)
    m2 = MonHoc.query.get(l2.mon_hoc_id)
    m1.so_tin_chi = 15
    m2.so_tin_chi = 5
    test_session.commit()

    dk1 = DangKy(sinh_vien_id=sample_student.id, lop_hoc_phan_id=l1.id)
    dk2 = DangKy(sinh_vien_id=sample_student.id, lop_hoc_phan_id=l2.id)
    l2.da_thi_giua_ky = True

    test_session.add_all([dk1, dk2])
    test_session.commit()

    fake_now = real_datetime(2020, 1, 1)
    datetime_mock = mocker.patch("ecourse.index.datetime")
    datetime_mock.now.return_value = fake_now
    datetime_mock.side_effect = lambda *args, **kwargs: real_datetime(*args, **kwargs)

    response = test_client.delete(f"/api/xoa_mon_da_dang_ky/{dk2.id}")
    data = response.get_json()

    assert response.status_code == 200
    assert data["status"] == 400
    assert DangKy.query.count() == 2
    assert "điểm" in data["message"].lower() or "giữa kỳ" in data["message"].lower()

if __name__ == '__main__':
    unittest.main()
