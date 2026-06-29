from django.urls import path

from .views import UserLoginView, profile, register, user_logout 

app_name = "accounts"

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", user_logout, name="logout"), 
    path("profile/", profile, name="profile"),
]