from flask_admin import Admin, AdminIndexView
from flask_login import current_user, logout_user
from ecourse import app, dao
from flask_admin.contrib.sqla import ModelView
from wtforms.validators import ValidationError
from ecourse.dao import count_lop_by_mon_hoc
from ecourse.models import MonHoc, LopHocPhan, UserRole, DangKy
from ecourse import db
from flask_admin import BaseView,expose
from flask import redirect, flash, url_for, request


class AdminView(ModelView):
    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return super(MyAdminIndexView, self).index()

        if current_user.user_role != UserRole.ADMIN:
            return redirect('/')

        return self.render('admin/index.html', mon_hoc_stats=count_lop_by_mon_hoc())
class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self) -> bool:
        return current_user.is_authenticated

class LopHocPhanView(AdminView):
    column_list = ['id','mon_hoc','so_luong_max', 'phong_hoc', 'ca_hoc', 'thu']

    form_columns = ['mon_hoc', 'hoc_ky', 'phong_hoc', 'thu', 'ca_hoc', 'so_luong_max', 'da_thi_giua_ky', 'active']

    def on_model_change(self, form, model, is_created):
        if model.so_luong_max > 50:
            raise ValueError("Số lượng sinh viên tối đa là 50")

        phong_chuan = model.phong_hoc.strip().upper() if model.phong_hoc else ""
        model.phong_hoc = phong_chuan

        thu_hien_tai = int(model.thu)
        ca_hien_tai = int(model.ca_hoc)
        hk_id_hien_tai = model.hoc_ky.id if model.hoc_ky else model.hoc_ky_id

        with db.session.no_autoflush:
            query = LopHocPhan.query.filter(
                LopHocPhan.hoc_ky_id == hk_id_hien_tai,
                LopHocPhan.phong_hoc == phong_chuan,
                LopHocPhan.thu == thu_hien_tai,
                LopHocPhan.ca_hoc == ca_hien_tai
            )

            if not is_created:
                query = query.filter(LopHocPhan.id != model.id)

            lop_trung = query.first()
            if lop_trung and lop_trung is not model:
                raise ValueError(f'Phòng {phong_chuan} đã có lớp id {lop_trung.id}')

    def handle_view_exception(self, exc):
        if isinstance(exc, ValueError):
            flash(str(exc), 'error')
            return True

        return super(LopHocPhanView, self).handle_view_exception(exc)
    def delete_model(self, model):
        sv_dang__ky = DangKy.query.filter_by(lop_hoc_phan_id = model.id).count()
        if sv_dang__ky > 0:
            flash(f'Không thể xóa, lớp đã có {sv_dang__ky} sinh viên', 'error')

            return False
        return super(LopHocPhanView, self).delete_model(model)

class ThongKeView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/stats.html',dang_ky_stats=dao.count_sv_by_lop())

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

admin = Admin(app=app, name="e-Course's Admin",template_mode='bootstrap4', index_view=MyAdminIndexView())
admin.add_view(AdminView(MonHoc,db.session, name= 'Môn Học'))
admin.add_view(LopHocPhanView(LopHocPhan,db.session, name = 'Lớp học phần'))
admin.add_view(ThongKeView(name='Thống kê'))
admin.add_view(LogoutView(name='Đăng xuất'))