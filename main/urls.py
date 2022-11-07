from django.urls import path
from .views import index, profile, updaterecord


urlpatterns = [
    path('', index, name='index'),
    path('profile/', profile, name='profile'),
    path('profile/updaterecord/<int:id>', updaterecord, name='updaterecord'),
]