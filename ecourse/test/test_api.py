import pytest
from ecourse.test.test_base import test_client,test_app


def test_api_dang_ky_thanh_cong(test_client,mocker):
    class FakeUser:
        is_authenticated = True
        id = 1

    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

    mock_dang_ky = mocker.patch("ecourse.dao.dang_ky_lop")

    response = test_client.post("/api/dang-ky", json = {
        "lop_hoc_phan_id":10

    })

    assert  response.status_code == 200
    data = response.get_json()

    assert data["status"]==200
    assert data["message"]=="Đăng ký học phần thành công"

    mock_dang_ky.assert_called_once_with(10)