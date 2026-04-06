
from flask_admin import Admin, AdminIndexView
from flask_login import current_user, logout_user
from ecourse import app, dao
from flask_admin.contrib.sqla import ModelView
from ecourse.models import MonHoc, LopHocPhan, UserRole
from ecourse import db
from flask_admin import BaseView,expose
from flask import redirect


class AdminView(ModelView):
    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html', mon_hoc_stats = dao.count_lop_by_mon_hoc())

    # def is_accessible(self):
    #     return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self) -> bool:
        return current_user.is_authenticated

class ProductView(AdminView):
    can_export = True
    column_searchable_list = ['name']

class ThongKeView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/stats.html',dang_ky_stats=dao.count_sv_by_lop())

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

admin = Admin(app=app, name="e-Course's Admin",template_mode='bootstrap4', index_view=MyAdminIndexView())
admin.add_view(AdminView(MonHoc,db.session, name= 'Môn Học'))
admin.add_view(AdminView(LopHocPhan,db.session, name = 'Lớp học phần'))
admin.add_view(ThongKeView(name='Thống kê'))
admin.add_view(LogoutView(name='Đăng xuất'))