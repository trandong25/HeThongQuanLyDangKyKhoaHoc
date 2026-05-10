import pytest

from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from ecourse import db, login_manager
from datetime import datetime,timedelta
from ecourse.models import HocKy, MonHoc, LopHocPhan, User, DangKy
from unittest.mock import patch




def create_app():
    app = Flask(__name__, template_folder="../templates")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["PAGE_SIZE"] = 2
    app.config['TESTING'] = True
    app.secret_key = '34y394yjsbdkjsdjksdh'
    db.init_app(app)

    login_manager.init_app(app)

    from ecourse.index import register_route
    register_route(app)

    return app

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
def test_app():
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def test_client(test_app):
    return test_app.test_client()

@pytest.fixture
def test_session(test_app):
    yield db.session
    db.session.rollback()

@pytest.fixture
def sample_student(test_session):
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
def mock_login_user(mocker, sample_student):
    class FakeUser:
        is_authenticated = True
        id = sample_student.id

    fake_user = FakeUser()

    mocker.patch("flask_login.utils._get_user", return_value=fake_user)
    mocker.patch("ecourse.index.current_user", new=fake_user)
    mocker.patch("ecourse.dao.current_user", new=fake_user)

    return fake_user

# @pytest.fixture
# def driver():
#     service = Service(executable_path='../.venv/chromedriver.exe')
#     driver = webdriver.Chrome(service=service)
#     yield driver
#     driver.quit()

@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--headless")  # chạy CI
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.implicitly_wait(5)

    yield driver

    driver.quit()