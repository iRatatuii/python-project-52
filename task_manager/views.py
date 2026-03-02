from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views import View


class IndexView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "index.html")


class UserLoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "login.html")

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Вы успешно вошли в систему")
            return redirect("/")
        else:
            messages.error(request, "Неверное имя пользователя или пароль")
            return render(request, "login.html")


class UserLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "Вы успешно вышли из системы")
        return redirect("/")


class UserCreateView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "registration.html")

    def post(self, request, *args, **kwargs):
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Валидация
        errors = []

        if not username:
            errors.append("Имя пользователя обязательно")

        if User.objects.filter(username=username).exists():
            errors.append("Пользователь с таким именем уже существует")

        if not password1:
            errors.append("Пароль обязателен")

        if password1 != password2:
            errors.append("Пароли не совпадают")

        if len(password1) < 3:
            errors.append("Пароль должен содержать минимум 3 символа")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, "registration.html")

        # Создание пользователя
        user = User.objects.create_user(
            username=username,
            password=password1,
            first_name=first_name,
            last_name=last_name,
        )

        messages.success(request, "Регистрация прошла успешно")
        return redirect("/")
