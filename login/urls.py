from django.urls import path
from .views import loginPage, registerPage, logoutPage, ForgetPassword, ChangePassword

urlpatterns = [
    path('', loginPage, name='login'),
    path('auth/', registerPage, name='auth'),
    path('forget-password/' , ForgetPassword , name="forget_password"),
    path('change-password/<token>/' , ChangePassword , name="change_password"),
    path('logoutPage/', logoutPage, name='logoutPage'),
]