from django.urls import path
from .views import index, profile, updaterecord, PasswordChangeView


urlpatterns = [
    path('', index, name='index'),
    path('profile/', profile, name='profile'),
    path('profile/updaterecord/<int:id>', updaterecord, name='updaterecord'),
    path('profile/updatepassword/', PasswordChangeView.as_view(template_name="main/profile.html"), name='updatepassword'),
]