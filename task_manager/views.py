from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .models import Label, Status, Task


class IndexView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "index.html")


class TaskListView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        tasks = (
            Task.objects.all()
            .select_related("status", "author", "executor")
            .prefetch_related("labels")
        )

        # Фильтрация
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
    login_url = "/login/"

    def get(self, request, pk, *args, **kwargs):
        task = get_object_or_404(
            Task.objects.select_related(
                "status", "author", "executor"
            ).prefetch_related("labels"),
            pk=pk,
        )
        return render(request, "task_detail.html", {"task": task})


class TaskCreateView(LoginRequiredMixin, View):
    login_url = "/login/"

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

        # Валидация
        errors = []

        if not name:
            errors.append("Название задачи обязательно")

        if not status_id:
            errors.append("Статус обязателен")

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect("/tasks/create/")

        # Создание задачи
        task = Task.objects.create(
            name=name,
            description=description,
            status_id=status_id,
            author=request.user,
            executor_id=executor_id if executor_id else None,
        )

        # Добавление меток
        if label_ids:
            task.labels.set(label_ids)

        messages.success(request, "Задача успешно создана")
        return redirect("/tasks/")


class TaskUpdateView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk)

        if not request.user.is_superuser and task.author != request.user:
            messages.error(request, "Задачу может редактировать только её автор")
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
            messages.error(request, "Задачу может редактировать только её автор")
            return redirect("/tasks/")
        
        name = request.POST.get("name")
        description = request.POST.get("description", "")
        status_id = request.POST.get("status")
        executor_id = request.POST.get("executor")
        label_ids = request.POST.getlist("labels")

        # Валидация
        errors = []

        if not name:
            errors.append("Название задачи обязательно")

        if not status_id:
            errors.append("Статус обязателен")

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect(f"/tasks/{pk}/update/")

        # Обновление задачи
        task.name = name
        task.description = description
        task.status_id = status_id
        task.executor_id = executor_id if executor_id else None
        task.save()

        # Обновление меток
        task.labels.set(label_ids)

        messages.success(request, "Задача успешно изменена")
        return redirect("/tasks/")


class TaskDeleteView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk)

        if not request.user.is_superuser and task.author != request.user:
            messages.error(request, "Задачу может удалить только её автор")
            return redirect("/tasks/")

        return render(request, "task_delete.html", {"task": task})

    def post(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk)

        if not request.user.is_superuser and task.author != request.user:
            messages.error(request, "Задачу может удалить только её автор")
            return redirect("/tasks/")
        task.delete()
        messages.success(request, "Задача успешно удалена")
        return redirect("/tasks/")


class LabelListView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        labels = Label.objects.all().order_by("id")
        return render(request, "labels.html", {"labels": labels})


class LabelCreateView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        return render(request, "label_create.html")

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")

        if not name:
            messages.error(request, "Имя метки обязательно")
            return render(request, "label_create.html")

        if Label.objects.filter(name=name).exists():
            messages.error(request, "Метка с таким именем уже существует")
            return render(request, "label_create.html")

        Label.objects.create(name=name)
        messages.success(request, "Метка успешно создана")
        return redirect("/labels/")


class LabelUpdateView(LoginRequiredMixin, View):
    login_url = "/login/"

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
            messages.error(request, "Метка с таким именем уже существует")
            return render(request, "label_update.html", {"label": label})

        label.name = name
        label.save()

        messages.success(request, "Метка успешно изменена")
        return redirect("/labels/")


class LabelDeleteView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, pk, *args, **kwargs):
        label = get_object_or_404(Label, pk=pk)
        # Проверяем, есть ли задачи с этой меткой
        if label.tasks.exists():
            messages.error(
                request,
                "Невозможно удалить метку, потому что она используется в задачах",
            )
            return redirect("/labels/")
        return render(request, "label_delete.html", {"label": label})

    def post(self, request, pk, *args, **kwargs):
        label = get_object_or_404(Label, pk=pk)
        # Проверяем, есть ли задачи с этой меткой
        if label.tasks.exists():
            messages.error(
                request,
                "Невозможно удалить метку, потому что она используется в задачах",
            )
            return redirect("/labels/")
        label.delete()
        messages.success(request, "Метка успешно удалена")
        return redirect("/labels/")


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
        if status.tasks.exists():
            messages.error(
                request,
                "Невозможно удалить статус, потому что он используется в задачах",
            )
            return redirect("/statuses/")

        return render(request, "status_delete.html", {"status": status})
        return render(request, "status_delete.html", {"status": status})

    def post(self, request, pk, *args, **kwargs):
        status = get_object_or_404(Status, pk=pk)
        if status.tasks.exists():
            messages.error(
                request,
                "Невозможно удалить статус, потому что он используется в задачах",
            )
            return redirect("/statuses/")
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
    def post(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "Вы успешно вышли из системы")
        return redirect("/")

    def get(self, request, *args, **kwargs):
        # Добавляем поддержку GET для отладки
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
        return redirect("/login/")


class UserUpdateView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)

        # Проверка прав: пользователь может редактировать только себя
        if not request.user.is_superuser and request.user.id != user.id:
            messages.error(
                request, "У вас нет прав для редактирования этого пользователя"
            )
            return redirect("/users/")

        return render(request, "user_update.html", {"user": user})

    def post(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)

        # Проверка прав
        if not request.user.is_superuser and request.user.id != user.id:
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
        if not request.user.is_superuser and request.user.id != user.id:
            messages.error(request, 'У вас нет прав для удаления этого пользователя')
            return redirect('/users/')
        
        # Проверяем, есть ли задачи, где пользователь является автором или исполнителем
        if user.authored_tasks.exists() or user.executed_tasks.exists():
            messages.error(
                request,
                "Невозможно удалить пользователя, потому что он связан с задачами",
            )
            return redirect("/users/")

        return render(request, "user_delete.html", {"user": user})

    def post(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)

        # Проверка прав
        if not request.user.is_superuser and request.user.id != user.id:
            messages.error(request, 'У вас нет прав для удаления этого пользователя')
            return redirect('/users/')
        
        # Проверяем, есть ли задачи, где пользователь является автором или исполнителем
        if user.authored_tasks.exists() or user.executed_tasks.exists():
            messages.error(
                request,
                "Невозможно удалить пользователя, потому что он связан с задачами",
            )
            return redirect("/users/")
        
        user.delete()
        messages.success(request, "Пользователь успешно удален")
        return redirect("/users/")
