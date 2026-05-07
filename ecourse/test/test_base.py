import pytest
from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from ecourse import db, login_manager
from ecourse.index import register_route


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["PAGE_SIZE"] = 2
    app.config['TESTING'] = True
    app.secret_key = '34y394yjsbdkjsdjksdh'
    db.init_app(app)

    login_manager.init_app(app)

    register_route(app)

    return app

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
def driver():
    service = Service(executable_path='../.venv/chromedriver.exe')
    driver = webdriver.Chrome(service=service)
    yield driver
    driver.quit()