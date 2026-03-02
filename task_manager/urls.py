from django.urls import path

from .views import (
    IndexView,
    StatusCreateView,
    StatusDeleteView,
    StatusListView,
    StatusUpdateView,
    UserCreateView,
    UserDeleteView,
    UserListView,
    UserLoginView,
    UserLogoutView,
    UserUpdateView,
)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("users/", UserListView.as_view(), name="users"),
    path("users/create/", UserCreateView.as_view(), name="user_create"),
    path("users/<int:pk>/update/", UserUpdateView.as_view(), name="user_update"),
    path("users/<int:pk>/delete/", UserDeleteView.as_view(), name="user_delete"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),

    # Status URLs
    path("statuses/", StatusListView.as_view(), name="statuses"),
    path("statuses/create/", StatusCreateView.as_view(), name="status_create"),
    path("statuses/<int:pk>/update/", StatusUpdateView.as_view(), name="status_update"),
    path("statuses/<int:pk>/delete/", StatusDeleteView.as_view(), name="status_delete"),
]
