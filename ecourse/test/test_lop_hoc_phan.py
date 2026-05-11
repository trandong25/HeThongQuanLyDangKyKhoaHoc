import pytest
from ecourse.models import LopHocPhan, MonHoc, HocKy, DangKy, User
from ecourse.admin import LopHocPhanView
from datetime import datetime, date
from unittest.mock import patch
from ecourse.test.test_base import test_session, test_app


def test_tao_lop_max_50(test_session):
    view = LopHocPhanView(LopHocPhan, test_session)

    lop = LopHocPhan(
        mon_hoc_id=1,
        hoc_ky_id=1,
        so_luong_max=60,
        phong_hoc="A101",
        thu=2,
        ca_hoc=1
    )

    with pytest.raises(ValueError):
        view.on_model_change(None, lop, True)


def test_trung_phong_fail(test_session):
    view = LopHocPhanView(LopHocPhan, test_session)

    hk = HocKy(
        name="HK1",
        ngay_bat_dau=date.today(),
        han_dang_ky=datetime.now()
    )
    test_session.add(hk)

    mon = MonHoc(name="Python", so_tin_chi=3)
    test_session.add(mon)
    test_session.commit()

    lop1 = LopHocPhan(
        mon_hoc_id=mon.id,
        hoc_ky_id=hk.id,
        so_luong_max=40,
        phong_hoc="A101",
        thu=2,
        ca_hoc=1
    )
    test_session.add(lop1)
    test_session.commit()

    lop2 = LopHocPhan(
        mon_hoc_id=mon.id,
        hoc_ky_id=hk.id,
        so_luong_max=40,
        phong_hoc="A101",
        thu=2,
        ca_hoc=1
    )

    with pytest.raises(ValueError):
        view.on_model_change(None, lop2, True)


def test_xoa_lop_co_sv_fail(test_session):
    view = LopHocPhanView(LopHocPhan, test_session)

    hk = HocKy(
        name="HK1",
        ngay_bat_dau=date.today(),
        han_dang_ky=datetime.now()
    )
    test_session.add(hk)

    mon = MonHoc(name="Python", so_tin_chi=3)
    test_session.add(mon)
    test_session.commit()

    lop = LopHocPhan(
        mon_hoc_id=mon.id,
        hoc_ky_id=hk.id,
        phong_hoc="A101",
        thu=2,
        ca_hoc=1
    )
    test_session.add(lop)
    test_session.commit()

    sv = User(name="SV", username="sv1", password="123")
    test_session.add(sv)
    test_session.commit()

    dk = DangKy(sinh_vien_id=sv.id, lop_hoc_phan_id=lop.id)
    test_session.add(dk)
    test_session.commit()

    with patch("ecourse.admin.flash") as mock_flash:
        result = view.delete_model(lop)

    assert result is False
    mock_flash.assert_called()