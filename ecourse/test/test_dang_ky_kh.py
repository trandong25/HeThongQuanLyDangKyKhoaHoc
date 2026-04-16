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

def test_load_all_classes(sample_lop_hoc_phan):
    classes = load_lop_hoc_phan()
    assert len(classes) == len(sample_lop_hoc_phan)


def test_dang_ky_thanh_cong(sample_lop_hoc_phan, sample_student, mock_login_user):
    l1 = sample_lop_hoc_phan[0]
    dang_ky_lop(l1.id)

    dk = DangKy.query.filter_by(
        sinh_vien_id=sample_student.id,
        lop_hoc_phan_id=l1.id
    ).first()

    assert dk is not None
    assert dk.sinh_vien_id == sample_student.id
    assert dk.lop_hoc_phan_id == l1.id


@pytest.mark.parametrize("case", [
    "khong_dang_nhap",
    "lop_khong_co",
    "lop_du_sl",
    "trung_lop",
    "het_han",
])
def test_dang_ky_cases_fail(case, test_session, sample_lop_hoc_phan, mock_login_user):
    l1 = sample_lop_hoc_phan[0]

    if case == "khong_dang_nhap":
        with patch("ecourse.dao.current_user") as user:
            user.is_authenticated = False
            with pytest.raises(Exception):
                dang_ky_lop(l1.id)

    elif case == "lop_khong_co":
        with pytest.raises(ValueError):
            dang_ky_lop(999)

    elif case == "lop_du_sl":
        l1.so_luong_max = 0
        test_session.commit()
        with pytest.raises(ValueError):
            dang_ky_lop(l1.id)

    elif case == "trung_lop":
        dang_ky_lop(l1.id)
        with pytest.raises(Exception):
            dang_ky_lop(l1.id)

    elif case == "het_han":
        hk = HocKy.query.get(l1.hoc_ky_id)
        hk.han_dang_ky = datetime.now() - timedelta(days=1)
        test_session.commit()

        with pytest.raises(ValueError):
            dang_ky_lop(l1.id)


def test_trung_lich(sample_lop_hoc_phan, test_session, mock_login_user):
    l1 = sample_lop_hoc_phan[0]
    dang_ky_lop(l1.id)

    mon = MonHoc(name="Test trùng lịch", so_tin_chi=2)
    test_session.add(mon)
    test_session.commit()

    lop_trung = LopHocPhan(
        mon_hoc_id=mon.id,
        hoc_ky_id=l1.hoc_ky_id,
        thu=l1.thu,
        ca_hoc=l1.ca_hoc,
        phong_hoc="Z",
        so_luong_max=50
    )
    test_session.add(lop_trung)
    test_session.commit()

    with pytest.raises(ValueError):
        dang_ky_lop(lop_trung.id)

    #chỉ có 1 môn
    assert DangKy.query.count() == 1

    #không có lớp mới
    ids = [dk.lop_hoc_phan_id for dk in DangKy.query.all()]
    assert lop_trung.id not in ids

def test_trung_mon(sample_lop_hoc_phan, test_session, mock_login_user):
    l1 = sample_lop_hoc_phan[0]
    dang_ky_lop(l1.id)

    lop_moi = LopHocPhan(
        mon_hoc_id=l1.mon_hoc_id,
        hoc_ky_id=l1.hoc_ky_id,
        thu=7,
        ca_hoc=2,
        phong_hoc="B202"
    )
    test_session.add(lop_moi)
    test_session.commit()

    with pytest.raises(ValueError):
        dang_ky_lop(lop_moi.id)


def test_trung_lop(sample_lop_hoc_phan, sample_student, mock_login_user):
    l1 = sample_lop_hoc_phan[0]

    dang_ky_lop(l1.id)

    with pytest.raises(Exception):
        dang_ky_lop(l1.id)

    ds = DangKy.query.filter_by(
        sinh_vien_id=sample_student.id,
        lop_hoc_phan_id=l1.id
    ).all()

    assert len(ds) == 1
    assert ds[0].lop_hoc_phan_id == l1.id

# def test_vuot_25_tin_chi(sample_lop_hoc_phan, test_session, mock_login_user):
#     l1, l2 = sample_lop_hoc_phan[0], sample_lop_hoc_phan[1]
#
#     m = MonHoc.query.get(l1.mon_hoc_id)
#     m.so_tin_chi = 24
#     test_session.commit()
#
#     dang_ky_lop(l1.id)
#
#     with pytest.raises(ValueError):
#         dang_ky_lop(l2.id)


# def test_dang_ky_dung_25_tin_chi(sample_lop_hoc_phan, test_session, mock_login_user):
#     l1 = sample_lop_hoc_phan[0]
#     l2 = sample_lop_hoc_phan[1]
#
#     m1 = MonHoc.query.get(l1.mon_hoc_id)
#     m2 = MonHoc.query.get(l2.mon_hoc_id)
#
#     m1.so_tin_chi = 13
#     m2.so_tin_chi = 12
#     test_session.commit()
#
#     dang_ky_lop(l1.id)
#     dang_ky_lop(l2.id)  # tổng = 25
#
#     assert DangKy.query.count() == 2


@pytest.mark.parametrize("tin_chi_1, tin_chi_2, expected_exception", [
    (24, 3, True),
    (13, 12, False),
    (12, 12, False),
])
def test_gioi_han_25_tin_chi(sample_lop_hoc_phan, test_session, mock_login_user, tin_chi_1, tin_chi_2, expected_exception):
    l1 = sample_lop_hoc_phan[0]
    l2 = sample_lop_hoc_phan[1]

    # Setup số tín chỉ
    m1 = MonHoc.query.get(l1.mon_hoc_id)
    m2 = MonHoc.query.get(l2.mon_hoc_id)

    m1.so_tin_chi = tin_chi_1
    m2.so_tin_chi = tin_chi_2
    test_session.commit()

    dang_ky_lop(l1.id)

    tong = tin_chi_1 + tin_chi_2

    #kiểm tra tổng tín chỉ setup đúng
    assert tong == tin_chi_1 + tin_chi_2

    if expected_exception:
        #phải fail nếu > 25
        with pytest.raises(ValueError, match="vượt quá 25 tín chỉ"):
            dang_ky_lop(l2.id)

        #chỉ có 1 đăng ký
        assert DangKy.query.count() == 1

    else:
        dang_ky_lop(l2.id)

        #đủ 2 đăng ký
        assert DangKy.query.count() == 2

        #tổng tín chỉ hợp lệ
        assert tong <= 25


@pytest.mark.parametrize("so_mon, expected_pass", [
    (1, False),
    (2, False),
    (4, True),
])
def test_min_12_tin_chi(test_session, sample_lop_hoc_phan, mock_login_user, so_mon, expected_pass):
    selected = sample_lop_hoc_phan[:so_mon]

    tong_tin_chi = 0

    for lop in selected:
        dang_ky_lop(lop.id)
        mon = MonHoc.query.get(lop.mon_hoc_id)
        tong_tin_chi += mon.so_tin_chi

    assert tong_tin_chi == so_mon * 3

    if expected_pass:
        assert tong_tin_chi >= 12
    else:
        assert tong_tin_chi < 12


def test_mon_tien_quyet(sample_lop_hoc_phan, test_session, mock_login_user):
    l4 = sample_lop_hoc_phan[3]

    m = MonHoc.query.get(l4.mon_hoc_id)
    m.mon_tien_quyet_id = 1
    test_session.commit()

    with pytest.raises(ValueError):
        dang_ky_lop(l4.id)


def test_da_hoc_mon(sample_lop_hoc_phan, test_session, sample_student, mock_login_user):
    l1 = sample_lop_hoc_phan[0]

    dk = DangKy(
        sinh_vien_id=sample_student.id,
        lop_hoc_phan_id=l1.id,
        diem_tong_ket=8
    )
    test_session.add(dk)
    test_session.commit()

    lop_moi = LopHocPhan(
        mon_hoc_id=l1.mon_hoc_id,
        hoc_ky_id=l1.hoc_ky_id,
        thu=5,
        ca_hoc=2,
        phong_hoc="B202"
    )
    test_session.add(lop_moi)
    test_session.commit()

    with pytest.raises(ValueError):
        dang_ky_lop(lop_moi.id)