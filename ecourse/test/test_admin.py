import pytest
from ecourse.models import LopHocPhan, MonHoc, User, DangKy, HocKy, UserRole
from ecourse.admin import LopHocPhanView
from ecourse.test.test_base import test_client,test_app,test_session
from datetime import datetime,date
from unittest.mock import patch


def test_max_50_sv_tren(test_session):
    view = LopHocPhanView(LopHocPhan,test_session)

    lop = LopHocPhan(mon_hoc_id = 1, hoc_ky_id = 1, so_luong_max = 51,phong_hoc="A101", thu=2, ca_hoc=1)

    with pytest.raises(ValueError,match="Số lượng sinh viên phải từ 1 đến 50"):
        view.on_model_change(form=None,model=lop,is_created=True)

def test_min_0_sv_duoi(test_session):
    view = LopHocPhanView(LopHocPhan,test_session)
    lop = LopHocPhan(mon_hoc_id = 1, hoc_ky_id = 1, so_luong_max = 0, thu=2, ca_hoc=1)
    with pytest.raises(ValueError, match="Số lượng sinh viên phải từ 1 đến 50"):
        view.on_model_change(form=None,model=lop,is_created=True)


def test_hop_le_50_sv(test_session):
    view = LopHocPhanView(LopHocPhan, test_session)
    mon = MonHoc(id=1, name="Test", so_tin_chi=3)
    test_session.add(mon)
    test_session.commit()

    lop = LopHocPhan(mon_hoc_id=1, hoc_ky_id=1, so_luong_max=50, phong_hoc="A101", thu=2, ca_hoc=1)
    try:
        view.on_model_change(form=None, model=lop, is_created=True)
        is_success = True
    except ValueError:
        is_success = False

    assert is_success is True

def test_trung_phong(test_session):
    view = LopHocPhanView(LopHocPhan,test_session)

    mon = MonHoc(id=1, name="Lập trình Python", so_tin_chi =3)
    lop_1 = LopHocPhan(mon_hoc_id=1, hoc_ky_id=1, so_luong_max=51, phong_hoc="A101", thu=2, ca_hoc=1)
    test_session.add_all([mon, lop_1])
    test_session.commit()

    lop_2_trung = LopHocPhan(mon_hoc_id=1,hoc_ky_id = 1, so_luong_max=30, phong_hoc="A101", thu=2, ca_hoc=1)

    with pytest.raises(ValueError) as ex:
        view.on_model_change(form=None, model=lop_2_trung, is_created=True)

    assert "đã có lớp id" in str(ex.value)

def test_xoa_lop_co_sv(test_session):
    view = LopHocPhanView(LopHocPhan, test_session)

    hk = HocKy(
        id=1,
        name="Học kỳ 1 (2025-2026)",
        ngay_bat_dau=date(2025, 9, 5),
        han_dang_ky=datetime(2025, 8, 30, 23, 59)
    )
    mon = MonHoc(id=1, name="Python", so_tin_chi=3)

    lop = LopHocPhan(id=1, mon_hoc_id=1, hoc_ky_id=1, so_luong_max=40, phong_hoc="B205", thu=3, ca_hoc=1)
    sv = User(id=1, name="SV Test", username="sv1", password="123")
    dk = DangKy(sinh_vien_id=1, lop_hoc_phan_id=1)

    test_session.add_all([hk, mon, lop, sv, dk])
    test_session.commit()

    with patch("ecourse.admin.flash") as mock_flash:
        ketqua = view.delete_model(lop)

    assert ketqua is False
    mock_flash.assert_called()

def test_quyen_tao_lop_pass(test_session,mocker):
    class FakeAdmin:
        is_authenticated = True
        user_role = UserRole.ADMIN
    mocker.patch("ecourse.admin.current_user", new=FakeAdmin())

    view = LopHocPhanView(LopHocPhan, test_session)

    assert view.is_accessible() is True


def test_quyen_tao_lop_fail(test_session, mocker):
    class FakeStudent:
        is_authenticated = True
        user_role = UserRole.SINHVIEN

    mocker.patch("ecourse.admin.current_user", new=FakeStudent())

    view = LopHocPhanView(LopHocPhan, test_session)

    assert view.is_accessible() is False