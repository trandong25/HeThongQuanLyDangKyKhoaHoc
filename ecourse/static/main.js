function chonMonHoc(id, name, tinChi,thu,caHoc,phongHoc,btnElement) {
    fetch('/api/dang_ky_tam', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "id": id,
            "name": name,
            "tin_chi": tinChi,
            "thu": thu,
            "ca_hoc": caHoc,
            "phong_hoc": phongHoc
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 200) {

            alert("Đã thêm môn: " + name + " vào danh sách chờ xác nhận!");

            btnElement.innerText = "Đã ghi danh";
            btnElement.classList.remove("btn-outline-success");
            btnElement.classList.add("btn-success", "disabled");
            btnElement.disabled = true;

        } else {
            alert(data.err_msg);
        }
    })
    .catch(error => {
        console.error("Lỗi:", error);
        alert("Lỗi hệ thống! Vui lòng thử lại.");
    });
}

function xoaMonHoc(id) {
    if (confirm("Bạn có chắc chắn muốn xóa môn này khỏi danh sách chờ?")) {
        fetch('/api/xoa-mon-tam/' + id, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 200) {
            confirm(data.message)
                location.reload();
            } else {
                alert("Có lỗi xảy ra: " + data.err_msg);
            }
        })
        .catch(error => {
            console.error("Lỗi:", error);
            alert("Lỗi hệ thống!");
        });
    }
}
function xoaMonHocDaDangKy(id, tinChiMonNay, TONG_TC_DANG_CO, tinChiToiThieu) {
    if (confirm("Bạn có chắc chắn muốn HỦY ĐĂNG KÝ môn học này?")) {
        fetch('/api/xoa_mon_da_dang_ky/' + id, {
            method: 'DELETE'
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 200) {
                location.reload();
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error("Lỗi:", error);
            alert("Lỗi hệ thống! Vui lòng thử lại.");
        });
    }
}

function checkOut() {
    fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 200) {

            alert(data.message);
            location.reload();

        } else {

            alert(data.message);

        }
    })
    .catch(error => {
        console.error("Lỗi:", error);
        alert("Lỗi kết nối đến máy chủ!");

    });
}
function yeuCauDangNhap(){
    alert("Yêu cầu đăng nhập hệ thống để ghi danh !!!")
}
