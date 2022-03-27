from django.contrib import admin
from django.urls import path, include

from .views import *

urlpatterns = [
    path('', main, name="main"),
    path('register/', RegisterUser.as_view(), name="register"),
    path('login/', LoginUser.as_view(), name="login"),
]
