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