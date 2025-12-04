from django.contrib.admin import AdminSite
from .admin_forms import CustomAdminAuthenticationForm


class CustomAdminSite(AdminSite):
    """
    Custom admin site that uses our custom authentication form
    """
    login_form = CustomAdminAuthenticationForm
    login_template = 'admin/login.html'
    site_header = "SapaPDD Админ Панель"
    site_title = "SapaPDD Admin"
    index_title = "Добро пожаловать в панель администрирования"

