import unittest,pytest
from datetime import datetime, timedelta

from pytest_mock import mocker

from ecourse.test.test_base import test_app,test_client, test_session,mock_login_user,sample_student,sample_lop_hoc_phan
from ecourse.models import DangKy, MonHoc
from datetime import datetime as real_datetime



def test_huy_mon(test_client, test_session, sample_student, sample_lop_hoc_phan, mock_login_user,mocker):
    l1 = sample_lop_hoc_phan[0]
    l2 = sample_lop_hoc_phan[1]

    dk1 = DangKy(sinh_vien_id=sample_student.id, lop_hoc_phan_id=l1.id)
    dk2 = DangKy(sinh_vien_id=sample_student.id, lop_hoc_phan_id=l2.id)
    test_session.add_all([dk1, dk2])
    test_session.commit()

    MonHoc.query.get(l1.mon_hoc_id).so_tin_chi = 15
    MonHoc.query.get(l2.mon_hoc_id).so_tin_chi = 5
    test_session.commit()

    fake_now = real_datetime(2020, 1, 1)


    datetime_mock = mocker.patch("ecourse.index.datetime")
    datetime_mock.now.return_value = fake_now

    response = test_client.delete(f"/api/xoa_mon_da_dang_ky/{dk2.id}")
    data = response.get_json()

    assert response.status_code == 200
    assert data["status"] == 200
    assert DangKy.query.count() == 1

def test_huy_mon_duoi_12_tin_chi(test_client, test_session, sample_student, sample_lop_hoc_phan, mock_login_user, mocker):
    l1 = sample_lop_hoc_phan[0]
    MonHoc.query.get(l1.mon_hoc_id).so_tin_chi = 13

    dk = DangKy(sinh_vien_id=sample_student.id, lop_hoc_phan_id=l1.id)
    test_session.add(dk)
    test_session.commit()

    fake_now = real_datetime(2020, 1, 1)
    datetime_mock = mocker.patch("ecourse.index.datetime")
    datetime_mock.now.return_value = fake_now

    response = test_client.delete(f"/api/xoa_mon_da_dang_ky/{dk.id}")
    data = response.get_json()

    assert data['status'] == 400
    assert "tối thiểu" in data['message']
    assert DangKy.query.count() == 1

def test_huy_mon_qua_han_2_tuan(test_client, test_session, sample_student, sample_lop_hoc_phan, mocker,mock_login_user):
    dk = DangKy(sinh_vien_id=sample_student.id, lop_hoc_phan_id=sample_lop_hoc_phan[0].id)
    test_session.add(dk)
    test_session.commit()

    fake_now = datetime(2030, 1, 1)
    datetime_mock = mocker.patch("ecourse.index.datetime")
    datetime_mock.now.return_value = fake_now

    response = test_client.delete(f"/api/xoa_mon_da_dang_ky/{dk.id}")
    data = response.get_json()

    assert data["status"] == 400
    assert "Quá thời hạn" in data["message"]
    assert DangKy.query.count() == 1

def test_huy_mon_da_thi_giua_ky(test_client, test_session, mock_login_user, sample_student, sample_lop_hoc_phan, mocker):
    l1, l2 = sample_lop_hoc_phan[0], sample_lop_hoc_phan[1]

    MonHoc.query.get(l1.mon_hoc_id).so_tin_chi = 15
    MonHoc.query.get(l2.mon_hoc_id).so_tin_chi = 5
    l2.da_thi_giua_ky = True

    dk1 = DangKy(sinh_vien_id=sample_student.id, lop_hoc_phan_id=l1.id)
    dk2 = DangKy(sinh_vien_id=sample_student.id, lop_hoc_phan_id=l2.id)
    test_session.add_all([dk1, dk2])
    test_session.commit()

    fake_now = real_datetime(2020, 1, 1)
    datetime_mock = mocker.patch("ecourse.index.datetime")
    datetime_mock.now.return_value = fake_now

    res = test_client.delete(f"/api/xoa_mon_da_dang_ky/{dk2.id}")
    data = res.get_json()

    assert data['status'] == 400
    assert "giữa kỳ" in data['message'].lower() or "điểm" in data['message'].lower()
    assert DangKy.query.count() == 2


def test_xoa_mon_khong_ton_tai(test_client, mock_login_user,mocker,sample_student):
    # bo sung time
    fake_now = real_datetime(2020, 1, 1)
    datetime_mock = mocker.patch("ecourse.index.datetime")
    datetime_mock.now.return_value = fake_now

    res = test_client.delete("/api/xoa_mon_da_dang_ky/9999")
    data = res.get_json()

    assert data['status'] == 404
    assert "Không tìm thấy" in data['message']


def test_xoa_mon_khong_chinh_chu(test_client, test_session, mock_login_user, sample_lop_hoc_phan,sample_student,mocker):
    # bo sung time
    fake_now = real_datetime(2020, 1, 1)
    datetime_mock = mocker.patch("ecourse.index.datetime")
    datetime_mock.now.return_value = fake_now

    dk1 = DangKy(sinh_vien_id=99, lop_hoc_phan_id=sample_lop_hoc_phan[0].id)
    test_session.add(dk1)
    test_session.commit()

    res = test_client.delete(f"/api/xoa_mon_da_dang_ky/{dk1.id}")
    data = res.get_json()

    assert data['status'] == 403
    assert "Không có quyền" in data['message']

