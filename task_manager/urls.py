from django.urls import path

from .views import IndexView, UserCreateView, UserListView, UserLoginView, UserLogoutView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("users/", UserListView.as_view(), name="users"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("users/create/", UserCreateView.as_view(), name="register"),
]
