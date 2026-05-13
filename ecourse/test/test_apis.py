from ecourse.test.test_base import test_app,test_client,test_session,sample_lop_hoc_phan,sample_student,mock_login_user
from ecourse.models import DangKy


def test_api_dang_ky_tam_pass(test_client,sample_lop_hoc_phan,mock_login_user):
    l1 = sample_lop_hoc_phan[0]
    payload = {
         "id": l1.id,
         "name": "Toán cao cấp",
         "tin_chi": 3,
         "thu": l1.thu,
         "ca_hoc": l1.ca_hoc,
         "phong_hoc": l1.phong_hoc
    }

    response = test_client.post("/api/dang_ky_tam", json=payload)

    data = response.get_json()
    assert response.status_code == 200
    assert data['status'] == 200
    assert data['message'] == 'Đã thêm vào danh sách chờ'


    with test_client.session_transaction() as sess:
        cart = sess.get('cart', {})
        assert str(l1.id) in cart
        assert cart[str(l1.id)]['name'] == "Toán cao cấp"
#Đăng ký tạm trùng môn trong giỏ
def test_dang_ky_tam_gio_fail(test_client, mock_login_user,sample_lop_hoc_phan):
    l1 = sample_lop_hoc_phan[0]
    l2 = sample_lop_hoc_phan[1]

    l2.mon_hoc_id = l1.mon_hoc_id

    with test_client.session_transaction() as sess:
        sess['cart'] = {
            str(l1.id):{
                "id": str(l1.id),
                "name":"Môn Toán",
                "mon_hoc_id": str(l1.mon_hoc_id),
            }
        }

    payload = {"id":l2.id}
    res = test_client.post("api/dang_ky_tam", json = payload)
    data = res.get_json()

    assert data['status']==400
    assert "Môn này đã có trong danh sách" in data['err_msg']

#Test cho đăng ký tạm trùng môn đã xác nhận
def test_dang_ky_tam_xac_nhan_fail(test_client,mock_login_user,sample_lop_hoc_phan,test_session):
    l1 = sample_lop_hoc_phan[0]
    l2 = sample_lop_hoc_phan[1]

    l2.mon_hoc_id = l1.mon_hoc_id
    dk_chinh_thuc = DangKy(sinh_vien_id=1, lop_hoc_phan_id=l1.id)
    test_session.add(dk_chinh_thuc)
    test_session.commit()

    payload = {"id": l2.id}
    response = test_client.post("/api/dang_ky_tam", json=payload)
    data = response.get_json()

    assert data['status'] == 400
    assert "Bạn đã xác nhận đăng ký môn" in data['err_msg']

#Test api xóa môn tạm api/xoa_mon_tam
def test_xoa_mon_tam_pass(test_client,mock_login_user):
    with test_client.session_transaction() as sess:
        sess['cart'] ={
            "99" : {"id":"99", "name":"Môn test","tin_chi":3}
        }

    res = test_client.delete("/api/xoa-mon-tam/99")
    data= res.get_json()

    assert res.status_code ==200
    assert data['status'] == 200

    with test_client.session_transaction() as sess:
        assert "99" not in sess.get('cart', {})

def test_xoa_mon_tam_fail(test_client,mock_login_user):
    with test_client.session_transaction() as sess:
        sess['cart'] = {}

    response = test_client.delete("/api/xoa-mon-tam/999")
    data = response.get_json()

    assert data['status'] == 400
    assert "Môn học không tồn tại" in data['err_msg']

# Test api /api/checkOut
def test_checkout_thieu_tin_chi_fail(test_client,mock_login_user, sample_lop_hoc_phan):
    l1 = sample_lop_hoc_phan[0]
    with test_client.session_transaction() as sess:
        sess['cart'] = {
            str(l1.id): {"id": str(l1.id), "tin_chi": 3}
        }

    response = test_client.post("/api/checkout")
    data = response.get_json()

    assert data['status'] == 400
    assert "Bạn chưa chọn đủ 12 tín chỉ" in data['message']


def test_api_checkout_12_pass(test_client, test_session, mock_login_user, sample_student, sample_lop_hoc_phan):
    l1, l2, l3, l4 = sample_lop_hoc_phan[0:4]

    with test_client.session_transaction() as sess:
        sess['cart'] = {
            str(l1.id): {"id": str(l1.id), "name": l1.mon_hoc.name, "tin_chi": l1.mon_hoc.so_tin_chi, "thu": l1.thu,
                         "ca_hoc": l1.ca_hoc},
            str(l2.id): {"id": str(l2.id), "name": l2.mon_hoc.name, "tin_chi": l2.mon_hoc.so_tin_chi, "thu": l2.thu,
                         "ca_hoc": l2.ca_hoc},
            str(l3.id): {"id": str(l3.id), "name": l3.mon_hoc.name, "tin_chi": l3.mon_hoc.so_tin_chi, "thu": l3.thu,
                         "ca_hoc": l3.ca_hoc},
            str(l4.id): {"id": str(l4.id), "name": l4.mon_hoc.name, "tin_chi": l4.mon_hoc.so_tin_chi, "thu": l4.thu,
                         "ca_hoc": l4.ca_hoc}
        }

    response = test_client.post("/api/checkout")
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 200

    phieu_dk_cua_sv = DangKy.query.filter_by(sinh_vien_id=sample_student.id).all()
    assert len(phieu_dk_cua_sv) == 4

    with test_client.session_transaction() as sess:
        assert not sess.get('cart')


def test_checkout_25_tin_chi_pass(test_client, test_session, mock_login_user, sample_student,sample_lop_hoc_phan):
    l1, l2, l3 = sample_lop_hoc_phan[0:3]
    l1.mon_hoc.so_tin_chi = 10
    l2.mon_hoc.so_tin_chi = 10
    l3.mon_hoc.so_tin_chi = 5
    test_session.commit()

    with test_client.session_transaction() as sess:
        sess['cart'] = {
            str(l1.id): {"id": str(l1.id), "name": l1.mon_hoc.name, "tin_chi": 10, "thu": l1.thu, "ca_hoc": l1.ca_hoc},
            str(l2.id): {"id": str(l2.id), "name": l2.mon_hoc.name, "tin_chi": 10, "thu": l2.thu, "ca_hoc": l2.ca_hoc},
            str(l3.id): {"id": str(l3.id), "name": l3.mon_hoc.name, "tin_chi": 5, "thu": l3.thu, "ca_hoc": l3.ca_hoc}
        }

    response = test_client.post("/api/checkout")
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 200

    phieu_dk = DangKy.query.filter_by(sinh_vien_id=sample_student.id).all()
    assert len(phieu_dk) == 3


def test_checkout_26_tin_chi_fail(test_client, test_session, mock_login_user, sample_lop_hoc_phan):
    l1, l2, l3 = sample_lop_hoc_phan[0:3]
    l1.mon_hoc.so_tin_chi = 10
    l2.mon_hoc.so_tin_chi = 10
    l3.mon_hoc.so_tin_chi = 6
    test_session.commit()

    with test_client.session_transaction() as sess:
        sess['cart'] = {
            str(l1.id): {"id": str(l1.id), "name": l1.mon_hoc.name, "tin_chi": 10, "thu": l1.thu, "ca_hoc": l1.ca_hoc},
            str(l2.id): {"id": str(l2.id), "name": l2.mon_hoc.name, "tin_chi": 10, "thu": l2.thu, "ca_hoc": l2.ca_hoc},
            str(l3.id): {"id": str(l3.id), "name": l3.mon_hoc.name, "tin_chi": 6, "thu": l3.thu, "ca_hoc": l3.ca_hoc}
        }

    response = test_client.post("/api/checkout")
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 400
    assert "25 tín chỉ" in data['message'].lower() or "vượt quá" in data['message'].lower()

    assert DangKy.query.count() == 0