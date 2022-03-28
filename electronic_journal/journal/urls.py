from django.contrib import admin
from django.urls import path, include

from .views import *

urlpatterns = [
    path('', main, name="main"),
    # profile - own profile with all the information
    # profile/<int:pk> - another profile with only contact
    path('profile/', own_profile, name="own_profile"),
    path('profile/<int:pk>', profile, name="profile"),
    path('profile/change', change_profile, name="change_profile"),
    path('register/', RegisterUser.as_view(), name="register"),
    path('login/', LoginUser.as_view(), name="login"),
    path('logout/', logout_user, name="logout"),
]
