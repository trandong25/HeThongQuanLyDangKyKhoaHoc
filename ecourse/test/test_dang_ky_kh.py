from tkinter.font import names

import pytest
from datetime import datetime,timedelta
from ecourse.dao import load_lop_hoc_phan, dang_ky_lop
from ecourse.models import HocKy, MonHoc, LopHocPhan, User, DangKy
from unittest.mock import patch
from ecourse.test.test_base import test_app,test_client, test_session

@pytest.fixture
def sample_lop_hoc_phan(test_session):

    ngay_hien_tai = datetime.now()
    fake_han_dang_ky = ngay_hien_tai + timedelta(days=30)

    hk1 = HocKy(name="HK1", active=True, ngay_bat_dau=ngay_hien_tai, han_dang_ky=fake_han_dang_ky)
    hk2 = HocKy(name="HK2", active=True, ngay_bat_dau=ngay_hien_tai, han_dang_ky=fake_han_dang_ky)

    test_session.add_all([hk1,hk2])
    test_session.commit()

    m1 = MonHoc(name="Python cơ bản", so_tin_chi=3)
    m2 = MonHoc(name="Lập trình Python", so_tin_chi=3)
    m3 = MonHoc(name="Kiểm thử phần mềm", so_tin_chi=3)
    m4 = MonHoc(name="Toán rời rạc", so_tin_chi=3)
    test_session.add_all([m1, m2, m3, m4])
    test_session.commit()

    l1 = LopHocPhan(mon_hoc_id=m1.id, hoc_ky_id=hk1.id, so_luong_max=50, active=True, phong_hoc="A101", thu=2, ca_hoc=1)
    l2 = LopHocPhan(mon_hoc_id=m2.id, hoc_ky_id=hk1.id, so_luong_max=50, active=True, phong_hoc="B202", thu=3, ca_hoc=2)
    l3 = LopHocPhan(mon_hoc_id=m3.id, hoc_ky_id=hk1.id, so_luong_max=50, active=True, phong_hoc="C303", thu=4, ca_hoc=3)
    l4 = LopHocPhan(mon_hoc_id=m3.id, hoc_ky_id=hk2.id, so_luong_max=50, active=True, phong_hoc="D404", thu=5, ca_hoc=4)
    l5 = LopHocPhan(mon_hoc_id=m4.id, hoc_ky_id=hk2.id, so_luong_max=50, active=True, phong_hoc="E505", thu=6, ca_hoc=1)

    test_session.add_all([l1,l2,l3,l4,l5])
    test_session.commit()

    return [l1, l2, l3, l4, l5]

@pytest.fixture
def sample_student(test_session):
    """Tạo một sinh viên ảo để có ID mà đăng ký môn"""
    sv = User(
        name="Sinh Vien Test",
        username="sv_test_01",
        password="123",
        active=True
    )
    test_session.add(sv)
    test_session.commit()
    return sv

@pytest.fixture
def mock_login_user(sample_student):
    with patch("ecourse.dao.current_user") as mock_user:
        mock_user.is_authenticated = True
        mock_user.id = sample_student.id

        yield mock_user

def test_all(sample_lop_hoc_phan):
    actual_classes = load_lop_hoc_phan()
    assert  len(actual_classes) == len(sample_lop_hoc_phan)

def test_dang_ky_thanh_cong(sample_lop_hoc_phan,sample_student, mock_login_user):
    l1 = sample_lop_hoc_phan[0]

    dang_ky_lop(l1.id)

    phieu_dk = DangKy.query.filter_by(
        sinh_vien_id = sample_student.id,
        lop_hoc_phan_id = l1.id
    ).first()

    assert phieu_dk is not None

def test_dang_ky_lop_day_fail (test_session, sample_lop_hoc_phan,sample_student,mock_login_user):
    l2 = sample_lop_hoc_phan[1]

    l2.so_luong_max = 0
    test_session.commit()

    with pytest.raises(ValueError, match="đã đủ sĩ số"):
        dang_ky_lop(l2.id)

def test_dang_ky_trung_fail(sample_lop_hoc_phan, sample_student, mock_login_user):
    l3 = sample_lop_hoc_phan[2]

    dang_ky_lop(l3.id)

    with pytest.raises(Exception, match="Bạn đã đăng ký lớp học phần này rồi"):
        dang_ky_lop(l3.id)

    so_luong = DangKy.query.filter_by(
        sinh_vien_id = sample_student.id,
        lop_hoc_phan_id = l3.id
    ).count()

    assert 1 == so_luong

def test_dang_ky_mon_tien_quyet_fail(test_session,sample_lop_hoc_phan,sample_student, mock_login_user):
    l4 = sample_lop_hoc_phan[3]

    m4 = MonHoc.query.get(l4.mon_hoc_id)
    m4.mon_tien_quyet_id = 1
    test_session.commit()

    with pytest.raises(ValueError, match="Bạn chưa học môn tiên quyết"):
        dang_ky_lop(l4.id)

def test_dang_ky_khong_login(sample_lop_hoc_phan):
    l1 = sample_lop_hoc_phan[0]

    with patch("ecourse.dao.current_user") as mock_user:
        mock_user.is_authenticated = False

        with pytest.raises(Exception, match= "Chức năng cần đăng nhập để thực hiện"):
            dang_ky_lop(l1.id)

def test_dang_ky_sau_tg_fail(test_session,sample_lop_hoc_phan,mock_login_user):
    l1 = sample_lop_hoc_phan[0]

    hk1 = HocKy.query.get(l1.hoc_ky_id)
    hk1.han_dang_ky = datetime.now() - timedelta(days=1)
    test_session.commit()

    with pytest.raises(ValueError, match="Đã hết thời hạn đăng ký"):
        dang_ky_lop(l1.id)
def test_dang_ky_mon_da_hoc_fail(test_session,sample_lop_hoc_phan,sample_student,mock_login_user):
    l1 = sample_lop_hoc_phan[0]

    phieu_cu = DangKy(sinh_vien_id = sample_student.id, lop_hoc_phan_id = l1.id, diem_tong_ket = 7.0)
    test_session.add(phieu_cu)
    test_session.commit()

    hk_moi = HocKy(name = "HK A", active = True, ngay_bat_dau = datetime.now(), han_dang_ky = datetime.now() + timedelta(days=30))
    test_session.add(hk_moi)
    test_session.commit()

    l_moi = LopHocPhan(mon_hoc_id=l1.mon_hoc_id, hoc_ky_id=hk_moi.id, so_luong_max=50, active=True, phong_hoc="A102",
                       thu=5, ca_hoc=1)
    test_session.add(l_moi)
    test_session.commit()

    with pytest.raises(ValueError, match="Bạn đã học và thi đạt môn này rồi"):
        dang_ky_lop(l_moi.id)

def test_dang_ky_trung_lich_fail(test_session, sample_lop_hoc_phan, mock_login_user):
    l1 = sample_lop_hoc_phan[0] #t2, c1

    dang_ky_lop(l1.id)

    mon_moi = MonHoc(name="Môn test trùng lịch", so_tin_chi=2)
    test_session.add(mon_moi)
    test_session.commit()

    lop_trung = LopHocPhan(mon_hoc_id=mon_moi.id, hoc_ky_id=l1.hoc_ky_id, so_luong_max=50, active=True, phong_hoc="B101", thu=l1.thu, ca_hoc=l1.ca_hoc)
    test_session.add(lop_trung)
    test_session.commit()

    with pytest.raises(ValueError, match="Trùng lịch học"):
        dang_ky_lop(lop_trung.id)

def test_dang_ky_vuot_25_tin_chi_fail(test_session, sample_lop_hoc_phan, mock_login_user):
    l1 = sample_lop_hoc_phan[0]
    l2 = sample_lop_hoc_phan[1]

    m1 = MonHoc.query.get(l1.mon_hoc_id)
    m1.so_tin_chi = 23
    test_session.commit()

    dang_ky_lop(l1.id)

    with pytest.raises(ValueError, match="Bạn đã vượt quá 25 tín chỉ"):
        dang_ky_lop(l2.id)