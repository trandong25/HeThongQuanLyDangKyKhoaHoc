import pytest
from ecourse.dao import count_sv_by_lop,count_lop_hoc_phan
from datetime import datetime,timedelta
from ecourse.dao import load_lop_hoc_phan, dang_ky_lop
from ecourse.models import HocKy, MonHoc, LopHocPhan, User, DangKy
from unittest.mock import patch
from ecourse.test.test_base import test_app,test_client, test_session,sample_lop_hoc_phan,sample_student,mock_login_user



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

def test_vuot_25_tin_chi(sample_lop_hoc_phan, test_session, mock_login_user):
    l1, l2 = sample_lop_hoc_phan[0], sample_lop_hoc_phan[1]

    m = MonHoc.query.get(l1.mon_hoc_id)
    m.so_tin_chi = 24
    test_session.commit()

    dang_ky_lop(l1.id)

    with pytest.raises(ValueError):
        dang_ky_lop(l2.id)

def test_dang_ky_dung_25_tin_chi(sample_lop_hoc_phan, test_session, mock_login_user):
    l1 = sample_lop_hoc_phan[0]
    l2 = sample_lop_hoc_phan[1]

    m1 = MonHoc.query.get(l1.mon_hoc_id)
    m2 = MonHoc.query.get(l2.mon_hoc_id)

    m1.so_tin_chi = 13
    m2.so_tin_chi = 12
    test_session.commit()

    dang_ky_lop(l1.id)
    dang_ky_lop(l2.id)

    assert DangKy.query.count() == 2

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

def test_lop_khong_active(sample_lop_hoc_phan, test_session, mock_login_user):
    l1 = sample_lop_hoc_phan[0]
    l1.active = False
    test_session.commit()

    with pytest.raises(ValueError, match="bị khóa hoặc chưa mở"):
        dang_ky_lop(l1.id)


def test_hoc_ky_khong_active(sample_lop_hoc_phan, test_session, mock_login_user):
    l1 = sample_lop_hoc_phan[0]
    hk = HocKy.query.get(l1.hoc_ky_id)
    hk.active = False
    test_session.commit()

    with pytest.raises(ValueError, match="không trong thời gian"):
        dang_ky_lop(l1.id)

#Test hàm trong dao
def test_count_sv_by_lop(test_session,sample_lop_hoc_phan,sample_student):
    l1 = sample_lop_hoc_phan[0]
    dk = DangKy(sinh_vien_id = sample_student.id, lop_hoc_phan_id = l1.id)
    test_session.add(dk)
    test_session.commit()

    ket_qua = count_sv_by_lop()

    dict_ket_qua = {}

    for row in ket_qua:
        dict_ket_qua[row[0]] = row[2]

    assert dict_ket_qua[l1.id] == 1
    assert dict_ket_qua[sample_lop_hoc_phan[1].id] == 0


def test_count_lop_by_mon_hoc(test_session, test_app, sample_lop_hoc_phan):
    with test_app.app_context():
        from ecourse.dao import count_lop_by_mon_hoc

        m0 = MonHoc(name="Môn rỗng", so_tin_chi=2)
        test_session.add(m0)
        test_session.commit()

        ket_qua = count_lop_by_mon_hoc()

        dict_thong_ke = {}
        for row in ket_qua:
            dict_thong_ke[row[0]] = row[2]

        #m3 sample có 2 lớp
        m3_id = sample_lop_hoc_phan[2].mon_hoc_id
        assert dict_thong_ke[m3_id] == 2

        #m1 sample có 1 lớp
        m1_id = sample_lop_hoc_phan[0].mon_hoc_id
        assert dict_thong_ke[m1_id] == 1

        assert dict_thong_ke[m0.id] == 0

def test_load_lop_hoc_phan_search(test_session, sample_lop_hoc_phan):
    ket_qua = load_lop_hoc_phan(kw="Python")

    assert len(ket_qua) == 2
    for lop in ket_qua:
        assert "Python" in lop.mon_hoc.name

def test_load_lop_hoc_phan_page(test_session, test_app, sample_lop_hoc_phan):
    with test_app.app_context():
        test_app.config["PAGE_SIZE"] = 1

        page_1 = load_lop_hoc_phan(page=1)
        assert len(page_1) == 1

        page_2 = load_lop_hoc_phan(page=2)
        assert len(page_2) == 1
        assert page_1[0].id != page_2[0].id