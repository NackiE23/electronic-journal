from django.contrib import admin
from django.urls import path, include

from .views import *

urlpatterns = [
    path('', main, name="main"),
    path('create_new_user', RegisterUser.as_view(), name="create_new_user"),
]
