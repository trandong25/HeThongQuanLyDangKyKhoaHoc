from ecourse.test.test_base import mock_login_user,test_app,test_session, test_client, sample_lop_hoc_phan,sample_student

##Test register
def test_api_register_password_ko_khop(test_client):
    res = test_client.post("/register", data={
        "name": "Nguyen Van A",
        "username": "usermoi",
        "password": "123",
        "confirm": "456"
    })

    assert res.status_code == 200
    assert "Mật khẩu không khớp" in res.data.decode("utf-8")

def test_api_register_trung_username(test_client, mocker):
    mocker.patch("ecourse.index.dao.get_user_by_username", return_value=True)

    res = test_client.post("/register", data={
        "name": "Nguyen Van B",
        "username": "demodemo",
        "confirm": "123"
    })

    assert res.status_code == 200
    assert "Trùng username" in res.data.decode("utf-8")


def test_api_register_success(test_client, mocker):
    mocker.patch("ecourse.index.dao.get_user_by_username", return_value=None)

    mock_add = mocker.patch("ecourse.index.dao.add_user")

    res = test_client.post("/register", data={
        "name": "Nguyen Van C",
        "username": "nguyenvanc",
        "password": "aB@123456789",
        "confirm": "aB@123456789"
    })

    assert res.status_code == 302
    assert "/login" in res.location

#Test login, logout
#Test cho một tài khoản đã đăng nhập nhưng lại truy cập lại /login
def test_login_da_dang_nhap(test_client, mock_login_user):

    res = test_client.get("/login")

    assert res.status_code == 302
    assert res.location.endswith("/")

def test_login_pass(test_client,mocker):
    class FakeAuthUser:
        is_active = True
        is_authenticated = True
        is_anonymous = False
        def get_id(self): return "1"

    mocker.patch("ecourse.index.dao.auth_user", return_value=FakeAuthUser())

    res = test_client.post("/login", data={
        "username": "admin",
        "password": "123"
    })

    assert res.status_code == 302
    assert res.location == "/"

#Test login sai mật khẩu
def test_login_fail(test_client,mocker):
    mocker.patch("ecourse.index.dao.auth_user", return_value=None)

    res = test_client.post("/login", data={
        "username": "admin",
        "password": "wrong_password"
    })

    assert res.status_code == 200
    assert "Đăng nhập không thành công" in res.data.decode("utf-8")


def test_logout(test_client, mock_login_user):
    res = test_client.get("/logout")

    assert res.status_code == 302
    assert res.location == "/login"