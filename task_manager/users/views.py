from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from task_manager import constants

# URL константы
LOGIN_URL = "/login/"
USERS_URL = "/users/"


class UserListView(View):
    def get(self, request, *args, **kwargs):
        users = User.objects.all().order_by("id")
        return render(request, "users/users.html", {"users": users})


class UserLoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "users/login.html")

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, constants.SUCCESS_LOGIN)
            return redirect("/")
        else:
            messages.error(request, constants.ERROR_INVALID_CREDENTIALS)
            return render(request, "users/login.html")


class UserLogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, constants.SUCCESS_LOGOUT)
        return redirect("/")

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, constants.SUCCESS_LOGOUT)
        return redirect("/")


class UserCreateView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "users/registration.html")

    def post(self, request, *args, **kwargs):
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        errors = []

        if not username:
            errors.append("Имя пользователя обязательно")

        if User.objects.filter(username=username).exists():
            errors.append(constants.ERROR_USERNAME_EXISTS)

        if not password1:
            errors.append("Пароль обязателен")

        if password1 != password2:
            errors.append(constants.ERROR_PWD_MISMATCH)

        if len(password1) < 3:
            errors.append(constants.ERROR_PWD_SHORT)

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, "users/registration.html")

        User.objects.create_user(
            username=username,
            password=password1,
            first_name=first_name,
            last_name=last_name,
        )

        messages.success(request, constants.SUCCESS_REGISTRATION)
        return redirect("/login/")


class UserUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)

        if not request.user.is_superuser and request.user.id != user.id:
            messages.error(request, constants.ERROR_NO_RIGHTS)
            return redirect(USERS_URL)

        return render(request, "users/user_update.html", {"user": user})

    def _validate_user_data(self, user, post_data):
        """Валидация данных пользователя"""
        first_name = post_data.get("first_name")
        last_name = post_data.get("last_name")
        username = post_data.get("username")
        password1 = post_data.get("password1")
        password2 = post_data.get("password2")

        errors = []

        if not username:
            errors.append(constants.ERROR_NAME_REQUIRED)

        if (
            username != user.username
            and User.objects.filter(username=username).exists()
        ):
            errors.append(constants.ERROR_USERNAME_EXISTS)

        if password1 or password2:
            if not password1:
                errors.append("Пароль обязателен")
            elif password1 != password2:
                errors.append(constants.ERROR_PWD_MISMATCH)
            elif len(password1) < 3:
                errors.append(constants.ERROR_PWD_SHORT)

        return errors, {
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "password1": password1,
            "password2": password2,
        }

    def _update_user_data(self, user, data):
        """Обновление данных пользователя"""
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        user.username = data["username"]

        if data["password1"]:
            user.set_password(data["password1"])

        user.save()
        return data["password1"]

    def post(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)

        if not request.user.is_superuser and request.user.id != user.id:
            messages.error(request, constants.ERROR_NO_RIGHTS)
            return redirect(USERS_URL)

        errors, data = self._validate_user_data(user, request.POST)

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, "users/user_update.html", {"user": user})

        password_changed = self._update_user_data(user, data)

        if password_changed:
            messages.success(request, constants.SUCCESS_USER_UPDATED)
            logout(request)
            return redirect(LOGIN_URL)
        else:
            messages.success(request, constants.SUCCESS_USER_UPDATED)
            return redirect(USERS_URL)


class UserDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)

        if user.authored_tasks.exists() or user.executed_tasks.exists():
            messages.error(request, constants.ERROR_CANNOT_DELETE_USER)
            return redirect(USERS_URL)

        if not request.user.is_superuser and request.user.id != user.id:
            messages.error(request, constants.ERROR_NO_RIGHTS)
            return redirect(USERS_URL)

        return render(request, "users/user_delete.html", {"user": user})

    def post(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)

        if user.authored_tasks.exists() or user.executed_tasks.exists():
            messages.error(request, constants.ERROR_CANNOT_DELETE_USER)
            return redirect(USERS_URL)

        if not request.user.is_superuser and request.user.id != user.id:
            messages.error(request, constants.ERROR_NO_RIGHTS)
            return redirect(USERS_URL)

        user.delete()
        messages.success(request, constants.SUCCESS_USER_DELETED)
        return redirect(USERS_URL)
