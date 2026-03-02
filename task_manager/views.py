from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from .models import Status

class IndexView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "index.html")


class StatusListView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        statuses = Status.objects.all().order_by("id")
        return render(request, "statuses.html", {"statuses": statuses})


class StatusCreateView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        return render(request, "status_create.html")

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")

        if not name:
            messages.error(request, "Имя статуса обязательно")
            return render(request, "status_create.html")

        if Status.objects.filter(name=name).exists():
            messages.error(request, "Статус с таким именем уже существует")
            return render(request, "status_create.html")

        Status.objects.create(name=name)
        messages.success(request, "Статус успешно создан")
        return redirect("/statuses/")


class StatusUpdateView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, pk, *args, **kwargs):
        status = get_object_or_404(Status, pk=pk)
        return render(request, "status_update.html", {"status": status})

    def post(self, request, pk, *args, **kwargs):
        status = get_object_or_404(Status, pk=pk)
        name = request.POST.get("name")

        if not name:
            messages.error(request, "Имя статуса обязательно")
            return render(request, "status_update.html", {"status": status})

        if name != status.name and Status.objects.filter(name=name).exists():
            messages.error(request, "Статус с таким именем уже существует")
            return render(request, "status_update.html", {"status": status})

        status.name = name
        status.save()

        messages.success(request, "Статус успешно изменен")
        return redirect("/statuses/")


class StatusDeleteView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, pk, *args, **kwargs):
        status = get_object_or_404(Status, pk=pk)
        return render(request, "status_delete.html", {"status": status})

    def post(self, request, pk, *args, **kwargs):
        status = get_object_or_404(Status, pk=pk)
        status.delete()
        messages.success(request, "Статус успешно удален")
        return redirect("/statuses/")


class UserListView(View):
    def get(self, request, *args, **kwargs):
        users = User.objects.all().order_by("id")
        return render(request, "users.html", {"users": users})


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


class UserUpdateView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)

        # Проверка прав: пользователь может редактировать только себя
        if request.user.id != user.id:
            messages.error(
                request, "У вас нет прав для редактирования этого пользователя"
            )
            return redirect("/users/")

        return render(request, "user_update.html", {"user": user})

    def post(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)

        # Проверка прав
        if request.user.id != user.id:
            messages.error(
                request, "У вас нет прав для редактирования этого пользователя"
            )
            return redirect("/users/")

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Валидация
        errors = []

        if not username:
            errors.append("Имя пользователя обязательно")

        # Проверка уникальности username (если он изменился)
        if (
            username != user.username
            and User.objects.filter(username=username).exists()
        ):
            errors.append("Пользователь с таким именем уже существует")

        # Если пароль заполнен, проверяем его
        if password1 or password2:
            if not password1:
                errors.append("Пароль обязателен")
            elif password1 != password2:
                errors.append("Пароли не совпадают")
            elif len(password1) < 3:
                errors.append("Пароль должен содержать минимум 3 символа")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, "user_update.html", {"user": user})

        # Обновление данных
        user.first_name = first_name
        user.last_name = last_name
        user.username = username

        # Если пароль указан, обновляем его
        if password1:
            user.set_password(password1)

        user.save()

        # Если пароль был изменен, нужно перенаправить на страницу входа
        if password1:
            messages.success(
                request, "Пользователь успешно обновлен. Пожалуйста, войдите снова."
            )
            logout(request)
            return redirect("/login/")
        else:
            messages.success(request, "Пользователь успешно обновлен")
            return redirect("/users/")


class UserDeleteView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)

        # Проверка прав
        if request.user.id != user.id:
            messages.error(request, "У вас нет прав для удаления этого пользователя")
            return redirect("/users/")

        return render(request, "user_delete.html", {"user": user})

    def post(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)

        # Проверка прав
        if request.user.id != user.id:
            messages.error(request, "У вас нет прав для удаления этого пользователя")
            return redirect("/users/")

        user.delete()
        messages.success(request, "Пользователь успешно удален")
        return redirect("/users/")
