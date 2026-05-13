from locust import HttpUser, task, between
import random


class ECourseUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.login()

    def login(self):
        response = self.client.post("/login", data={
            "username": "student1",
            "password": "123456"
        })

        if response.status_code != 200:
            print("Login thất bại!")


    @task(3)
    def load_home_page(self):
        res = self.client.get("/")
        if res.status_code != 200:
            print("Lỗi load trang chủ")


    @task(2)
    def load_classes(self):
        res = self.client.get("/?page=1")

        if res.status_code != 200:
            print("Lỗi load danh sách lớp")


    @task(2)
    def add_to_cart(self):
        # giả lập chọn random lớp
        lop_id = random.randint(1, 10)

        data = {
            "id": lop_id,
            "name": f"Lop {lop_id}",
            "tin_chi": random.randint(2, 4),
            "thu": random.randint(2, 7),
            "ca_hoc": random.randint(1, 4),
            "phong_hoc": "A101"
        }

        res = self.client.post("/api/dang_ky_tam", json=data)

        if res.status_code != 200:
            print("Lỗi thêm vào giỏ")


    @task(1)
    def remove_from_cart(self):
        lop_id = random.randint(1, 10)

        res = self.client.delete(f"/api/xoa-mon-tam/{lop_id}")

        if res.status_code not in [200, 400]:
            print("Lỗi xóa môn")


    @task(2)
    def checkout(self):
        res = self.client.post("/api/checkout")

        if res.status_code not in [200, 400]:
            print("Lỗi checkout hệ thống")


    @task(1)
    def view_timetable(self):
        res = self.client.get("/timetable")

        if res.status_code != 200:
            print("Lỗi load timetable")


    @task(1)
    def view_register_page(self):
        res = self.client.get("/class_register")

        if res.status_code != 200:
            print("Lỗi load trang đăng ký")