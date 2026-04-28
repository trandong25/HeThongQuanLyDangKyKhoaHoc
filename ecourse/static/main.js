function dangKyMonHoc(lopHocPhanId){
    if(confirm("Bạn có chắc chắn muốn đăng ký lớp học phần này không?")){
        fetch('/api/dang-ky',{
            method: 'POST',
            headers:{
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'lop_hoc_phan_id': lopHocPhanId
            })
        }).then(response => response.json())
        .then(data =>{
            if (data.status === 200){
                location.reload();
            }
            else{
                alert("Không thể đăng ký" + data.err_msg);
            }
        })
        .catch(error => {
            console.error("Error: "+ error);
            alert("Đã xảy ra lỗi")
        })
    }
}


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
                location.reload();
            } else {
                alert("Có lỗi xảy ra: " + data.err_msg);
            }
        });
    }
}
function xoaMonHocDaDangKy(id, tinChiMonNay,TONG_TC_DANG_CO,tinChiToiThieu) {
    // 1. Kiểm tra ràng buộc TỐI THIỂU 12 TÍN CHỈ
    if ((TONG_TC_DANG_CO - tinChiMonNay) < tinChiToiThieu) {
        alert(`KHÔNG THỂ HỦY MÔN!\nTheo quy định, bạn phải có tối thiểu ${tinChiToiThieu} TC. Nếu hủy môn này, bạn chỉ còn ${TONG_TC_DANG_CO - tinChiMonNay} TC. Vui lòng đăng ký thêm môn khác trước khi hủy môn này.`);
        return; // Dừng luôn, không gửi request lên server
    }

    // 2. Nếu đủ điều kiện thì mới hỏi xác nhận
    if (confirm("Bạn có chắc chắn muốn HỦY ĐĂNG KÝ môn học này?")) {
        fetch('/api/xoa_mon_da_dang_ky/' + id, {
            method: 'DELETE'
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 200) {
                alert("Đã hủy môn học thành công!");
                location.reload();
            } else {
                alert("Lỗi: " + data.message);
            }
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
