from django.urls import path
from .views import index, partner


urlpatterns = [
    path('', index, name='index'),
    path('partner/', partner, name='partner'),
]