from django.urls import path
from .views import profile, updaterecord, PasswordChangeView


urlpatterns = [
    path('', profile, name='profile'),
    path('updaterecord/<int:id>', updaterecord, name='updaterecord'),
    path('updatepassword/', PasswordChangeView.as_view(template_name="main/profile.html"), name='updatepassword'),
]