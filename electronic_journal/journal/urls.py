from django.contrib import admin
from django.urls import path, include

from .views import *

urlpatterns = [
    path('', main, name="main"),
    path('profile/', own_profile, name="own_profile"),
    path('profile/<int:pk>/', profile, name="profile"),
    path('profile/edit/', UserEditView.as_view(), name="edit_profile"),
    path('group/<slug:group_slug>/', group, name="group"),
    path('register/', RegisterUser.as_view(), name="register"),
    path('login/', LoginUser.as_view(), name="login"),
    path('logout/', logout_user, name="logout"),
]
