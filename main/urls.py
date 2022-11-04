from django.urls import path
from .views import index, profile


urlpatterns = [
    path('', index, name='index'),
    path('profile/', profile, name='profile'),
]