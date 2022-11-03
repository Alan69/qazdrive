from django.urls import path
from .views import loginPage, registerPage, logoutPage

urlpatterns = [
    path('login/', loginPage, name='index'),
    path('auth/', registerPage, name='auth'),
    path('logoutPage/', logoutPage, name='logoutPage'),
]