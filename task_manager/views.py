from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .models import Label, Status, Task

# URL константы
LOGIN_URL = "/login/"
USERS_URL = "/users/"

# Сообщения об ошибках
ERROR_NO_RIGHTS = "У вас нет прав для редактирования этого пользователя"
ERROR_CANNOT_DELETE_USER = (
    "Невозможно удалить пользователя, потому что он связан с задачами"
)
ERROR_CANNOT_DELETE_STATUS = (
    "Невозможно удалить статус, потому что он используется в задачах"
)
ERROR_CANNOT_DELETE_LABEL = (
    "Невозможно удалить метку, потому что она используется в задачах"
)
ERROR_TASK_DELETE_RIGHTS = "Задачу может удалить только её автор"
ERROR_TASK_EDIT_RIGHTS = "Задачу может редактировать только её автор"
ERROR_INVALID_CREDENTIALS = "Неверное имя пользователя или пароль"
ERROR_NAME_REQUIRED = "Имя обязательно"
ERROR_STATUS_REQUIRED = "Статус обязателен"
ERROR_PWD_MISMATCH = "Пароли не совпадают"
ERROR_PWD_SHORT = "Пароль должен содержать минимум 3 символа"
ERROR_USERNAME_EXISTS = "Пользователь с таким именем уже существует"
ERROR_STATUS_EXISTS = "Статус с таким именем уже существует"
ERROR_LABEL_EXISTS = "Метка с таким именем уже существует"

# Сообщения об успехе
SUCCESS_LOGIN = "Вы успешно вошли в систему"
SUCCESS_LOGOUT = "Вы успешно вышли из системы"
SUCCESS_USER_UPDATED = "Пользователь успешно обновлен"
SUCCESS_USER_DELETED = "Пользователь успешно удален"
SUCCESS_STATUS_CREATED = "Статус успешно создан"
SUCCESS_STATUS_UPDATED = "Статус успешно изменен"
SUCCESS_STATUS_DELETED = "Статус успешно удален"
SUCCESS_LABEL_CREATED = "Метка успешно создана"
SUCCESS_LABEL_UPDATED = "Метка успешно изменена"
SUCCESS_LABEL_DELETED = "Метка успешно удалена"
SUCCESS_TASK_CREATED = "Задача успешно создана"
SUCCESS_TASK_UPDATED = "Задача успешно изменена"
SUCCESS_TASK_DELETED = "Задача успешно удалена"


class IndexView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "index.html")


class TaskListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tasks = (
            Task.objects.all()
            .select_related("status", "author", "executor")
            .prefetch_related("labels")
        )

        status_id = request.GET.get("status")
        executor_id = request.GET.get("executor")
        label_id = request.GET.get("label")
        self_tasks = request.GET.get("self_tasks")

        if status_id:
            tasks = tasks.filter(status_id=status_id)

        if executor_id:
            tasks = tasks.filter(executor_id=executor_id)

        if label_id:
            tasks = tasks.filter(labels__id=label_id)

        if self_tasks:
            tasks = tasks.filter(author=request.user)

        statuses = Status.objects.all()
        users = User.objects.all()
        labels = Label.objects.all()

        context = {
            "tasks": tasks,
            "statuses": statuses,
            "users": users,
            "labels": labels,
        }
        return render(request, "tasks.html", context)


class TaskDetailView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        task = get_object_or_404(
            Task.objects.select_related(
                "status", "author", "executor"
            ).prefetch_related("labels"),
            pk=pk,
        )
        return render(request, "task_detail.html", {"task": task})


class TaskCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        statuses = Status.objects.all()
        users = User.objects.all()
        labels = Label.objects.all()

        context = {
            "statuses": statuses,
            "users": users,
            "labels": labels,
        }
        return render(request, "task_create.html", context)

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")
        description = request.POST.get("description", "")
        status_id = request.POST.get("status")
        executor_id = request.POST.get("executor")
        label_ids = request.POST.getlist("labels")

        errors = []

        if not name:
            errors.append("Название задачи обязательно")

        if not status_id:
            errors.append(ERROR_STATUS_REQUIRED)

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect("/tasks/create/")

        task = Task.objects.create(
            name=name,
            description=description,
            status_id=status_id,
            author=request.user,
            executor_id=executor_id if executor_id else None,
        )

        if label_ids:
            task.labels.set(label_ids)

        messages.success(request, SUCCESS_TASK_CREATED)
        return redirect("/tasks/")


class TaskUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk)

        if not request.user.is_superuser and task.author != request.user:
            messages.error(request, ERROR_TASK_EDIT_RIGHTS)
            return redirect("/tasks/")

        statuses = Status.objects.all()
        users = User.objects.all()
        labels = Label.objects.all()

        context = {
            "task": task,
            "statuses": statuses,
            "users": users,
            "labels": labels,
        }
        return render(request, "task_update.html", context)

    def post(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk)

        if not request.user.is_superuser and task.author != request.user:
            messages.error(request, ERROR_TASK_EDIT_RIGHTS)
            return redirect("/tasks/")

        name = request.POST.get("name")
        description = request.POST.get("description", "")
        status_id = request.POST.get("status")
        executor_id = request.POST.get("executor")
        label_ids = request.POST.getlist("labels")

        errors = []

        if not name:
            errors.append("Название задачи обязательно")

        if not status_id:
            errors.append(ERROR_STATUS_REQUIRED)

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect(f"/tasks/{pk}/update/")

        task.name = name
        task.description = description
        task.status_id = status_id
        task.executor_id = executor_id if executor_id else None
        task.save()

        task.labels.set(label_ids)

        messages.success(request, SUCCESS_TASK_UPDATED)
        return redirect("/tasks/")


class TaskDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk)

        if not request.user.is_superuser and task.author != request.user:
            messages.error(request, ERROR_TASK_DELETE_RIGHTS)
            return redirect("/tasks/")

        return render(request, "task_delete.html", {"task": task})

    def post(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk)

        if not request.user.is_superuser and task.author != request.user:
            messages.error(request, ERROR_TASK_DELETE_RIGHTS)
            return redirect("/tasks/")
        task.delete()
        messages.success(request, SUCCESS_TASK_DELETED)
        return redirect("/tasks/")


class LabelListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        labels = Label.objects.all().order_by("id")
        return render(request, "labels.html", {"labels": labels})


class LabelCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, "label_create.html")

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")

        if not name:
            messages.error(request, "Имя метки обязательно")
            return render(request, "label_create.html")

        if Label.objects.filter(name=name).exists():
            messages.error(request, ERROR_LABEL_EXISTS)
            return render(request, "label_create.html")

        Label.objects.create(name=name)
        messages.success(request, SUCCESS_LABEL_CREATED)
        return redirect("/labels/")


class LabelUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        label = get_object_or_404(Label, pk=pk)
        return render(request, "label_update.html", {"label": label})

    def post(self, request, pk, *args, **kwargs):
        label = get_object_or_404(Label, pk=pk)
        name = request.POST.get("name")

        if not name:
            messages.error(request, "Имя метки обязательно")
            return render(request, "label_update.html", {"label": label})

        if name != label.name and Label.objects.filter(name=name).exists():
            messages.error(request, ERROR_LABEL_EXISTS)
            return render(request, "label_update.html", {"label": label})

        label.name = name
        label.save()

        messages.success(request, SUCCESS_LABEL_UPDATED)
        return redirect("/labels/")


class LabelDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        label = get_object_or_404(Label, pk=pk)
        # Проверяем, есть ли задачи с этой меткой
        if label.tasks.exists():
            messages.error(
                request,
                ERROR_CANNOT_DELETE_LABEL,
            )
            return redirect("/labels/")
        return render(request, "label_delete.html", {"label": label})

    def post(self, request, pk, *args, **kwargs):
        label = get_object_or_404(Label, pk=pk)
        # Проверяем, есть ли задачи с этой меткой
        if label.tasks.exists():
            messages.error(
                request,
                ERROR_CANNOT_DELETE_LABEL,
            )
            return redirect("/labels/")
        label.delete()
        messages.success(request, SUCCESS_LABEL_DELETED)
        return redirect("/labels/")


class StatusListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        statuses = Status.objects.all().order_by("id")
        return render(request, "statuses.html", {"statuses": statuses})


class StatusCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, "status_create.html")

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")

        if not name:
            messages.error(request, "Имя статуса обязательно")
            return render(request, "status_create.html")

        if Status.objects.filter(name=name).exists():
            messages.error(request, ERROR_STATUS_EXISTS)
            return render(request, "status_create.html")

        Status.objects.create(name=name)
        messages.success(request, SUCCESS_STATUS_CREATED)
        return redirect("/statuses/")


class StatusUpdateView(LoginRequiredMixin, View):
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
            messages.error(request, ERROR_STATUS_EXISTS)
            return render(request, "status_update.html", {"status": status})

        status.name = name
        status.save()

        messages.success(request, SUCCESS_STATUS_UPDATED)
        return redirect("/statuses/")


class StatusDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        status = get_object_or_404(Status, pk=pk)
        if status.tasks.exists():
            messages.error(
                request,
                ERROR_CANNOT_DELETE_STATUS,
            )
            return redirect("/statuses/")

        return render(request, "status_delete.html", {"status": status})
        return render(request, "status_delete.html", {"status": status})

    def post(self, request, pk, *args, **kwargs):
        status = get_object_or_404(Status, pk=pk)
        if status.tasks.exists():
            messages.error(
                request,
                ERROR_CANNOT_DELETE_STATUS,
            )
            return redirect("/statuses/")
        status.delete()
        messages.success(request, SUCCESS_STATUS_DELETED)
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
            messages.success(request, "SUCCESS_LOGIN")
            return redirect("/")
        else:
            messages.error(request, ERROR_INVALID_CREDENTIALS)
            return render(request, "login.html")


class UserLogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, SUCCESS_LOGOUT)
        return redirect("/")

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, SUCCESS_LOGOUT)
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

        errors = []

        if not username:
            errors.append("Имя пользователя обязательно")

        if User.objects.filter(username=username).exists():
            errors.append(ERROR_USERNAME_EXISTS)

        if not password1:
            errors.append("Пароль обязателен")

        if password1 != password2:
            errors.append(ERROR_PWD_MISMATCH)

        if len(password1) < 3:
            errors.append(ERROR_PWD_SHORT)

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, "registration.html")

        User.objects.create_user(
            username=username,
            password=password1,
            first_name=first_name,
            last_name=last_name,
        )

        messages.success(request, "Регистрация прошла успешно")
        return redirect("/login/")


class UserUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)

        if not request.user.is_superuser and request.user.id != user.id:
            messages.error(request, ERROR_NO_RIGHTS)
            return redirect(USERS_URL)

        return render(request, "user_update.html", {"user": user})

    def _validate_user_data(self, user, post_data):
        """Валидация данных пользователя"""
        first_name = post_data.get("first_name")
        last_name = post_data.get("last_name")
        username = post_data.get("username")
        password1 = post_data.get("password1")
        password2 = post_data.get("password2")

        errors = []

        if not username:
            errors.append(ERROR_NAME_REQUIRED)

        if (
            username != user.username
            and User.objects.filter(username=username).exists()
        ):
            errors.append(ERROR_USERNAME_EXISTS)

        if password1 or password2:
            if not password1:
                errors.append("Пароль обязателен")
            elif password1 != password2:
                errors.append(ERROR_PWD_MISMATCH)
            elif len(password1) < 3:
                errors.append(ERROR_PWD_SHORT)

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
            messages.error(request, ERROR_NO_RIGHTS)
            return redirect(USERS_URL)

        # Валидация
        errors, data = self._validate_user_data(user, request.POST)

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, "user_update.html", {"user": user})

        # Обновление данных
        password_changed = self._update_user_data(user, data)

        if password_changed:
            messages.success(request, SUCCESS_USER_UPDATED)
            logout(request)
            return redirect(LOGIN_URL)
        else:
            messages.success(request, SUCCESS_USER_UPDATED)
            return redirect(USERS_URL)


class UserDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)

        if not request.user.is_superuser and request.user.id != user.id:
            messages.error(
                request, "У вас нет прав для удаления этого пользователя"
            )
            return redirect("/users/")

        if user.authored_tasks.exists() or user.executed_tasks.exists():
            messages.error(
                request,
                ERROR_NO_RIGHTS,
            )
            return redirect("/users/")

        return render(request, "user_delete.html", {"user": user})

    def post(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)

        if not request.user.is_superuser and request.user.id != user.id:
            messages.error(
                request, "У вас нет прав для удаления этого пользователя"
            )
            return redirect("/users/")

        if user.authored_tasks.exists() or user.executed_tasks.exists():
            messages.error(
                request,
                ERROR_NO_RIGHTS,
            )
            return redirect("/users/")

        user.delete()
        messages.success(request, SUCCESS_USER_DELETED)
        return redirect("/users/")
