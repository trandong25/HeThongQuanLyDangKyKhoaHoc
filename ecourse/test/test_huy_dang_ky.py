import pytest
from datetime import datetime, timedelta
from ecourse.models import DangKy, LopHocPhan, HocKy, User
from unittest.mock import patch


def huy_dang_ky_gia_lap(dk, hoc_ky):
    if dk.sinh_vien_id != 1:
        raise Exception("Không phải sinh viên đăng ký")

    if datetime.now().date() > hoc_ky.ngay_bat_dau + timedelta(days=14):
        raise ValueError("Đã quá hạn hủy")

    if dk.lop_hoc_phan.da_thi_giua_ky:
        raise ValueError("Đã thi giữa kỳ")

    return True


def test_huy_thanh_cong(test_session):
    hk = HocKy(
        name="HK1",
        ngay_bat_dau=datetime.now().date(),
        han_dang_ky=datetime.now()
    )
    test_session.add(hk)
    test_session.commit()

    lop = LopHocPhan(mon_hoc_id=1, hoc_ky_id=hk.id, thu=2, ca_hoc=1, phong_hoc="A")
    test_session.add(lop)
    test_session.commit()

    dk = DangKy(sinh_vien_id=1, lop_hoc_phan_id=lop.id)
    test_session.add(dk)
    test_session.commit()

    assert huy_dang_ky_gia_lap(dk, hk) == True


def test_huy_sau_2_tuan_fail(test_session):
    hk = HocKy(
        name="HK1",
        ngay_bat_dau=datetime.now().date() - timedelta(days=20),
        han_dang_ky=datetime.now()
    )
    test_session.add(hk)
    test_session.commit()

    lop = LopHocPhan(mon_hoc_id=1, hoc_ky_id=hk.id, thu=2, ca_hoc=1, phong_hoc="A202")
    test_session.add(lop)
    test_session.commit()

    dk = DangKy(sinh_vien_id=1, lop_hoc_phan_id=lop.id)
    test_session.add(dk)
    test_session.commit()

    with pytest.raises(ValueError):
        huy_dang_ky_gia_lap(dk, hk)


def test_huy_sau_midterm_fail(test_session):
    hk = HocKy(
        name="HK1",
        ngay_bat_dau=datetime.now().date(),
        han_dang_ky=datetime.now()
    )
    test_session.add(hk)
    test_session.commit()

    lop = LopHocPhan(
        mon_hoc_id=1,
        hoc_ky_id=hk.id,
        thu=2,
        ca_hoc=1,
        phong_hoc="A302",
        da_thi_giua_ky=True
    )
    test_session.add(lop)
    test_session.commit()

    dk = DangKy(sinh_vien_id=1, lop_hoc_phan_id=lop.id)
    test_session.add(dk)
    test_session.commit()

    with pytest.raises(ValueError):
        huy_dang_ky_gia_lap(dk, hk)