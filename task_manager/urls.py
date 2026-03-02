from django.urls import path

from .views import IndexView, UserCreateView, UserLoginView, UserLogoutView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("users/create/", UserCreateView.as_view(), name="register"),
]
