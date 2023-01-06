from django.urls import  path
from .views import *

urlpatterns = [
    path('post_order/<str:product>/<int:sum>', post_order, name ="post_order"),
    path('check_order/', check_order, name="check_order"),
    path('send_subs_req/<str:subsname>/', send_subs_req, name="send_subs_req"),
]