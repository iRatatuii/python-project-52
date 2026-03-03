from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .. import constants
from ..models import Label, Status, Task


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

        if status_id and status_id.isdigit():
            tasks = tasks.filter(status_id=status_id)

        if executor_id and executor_id.isdigit():
            tasks = tasks.filter(executor_id=executor_id)

        if label_id and label_id.isdigit():
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
        return render(request, "tasks/tasks.html", context)


class TaskDetailView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        task = get_object_or_404(
            Task.objects.select_related(
                "status", "author", "executor"
            ).prefetch_related("labels"),
            pk=pk,
        )
        return render(request, "tasks/task_detail.html", {"task": task})


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
        return render(request, "tasks/task_create.html", context)

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")
        description = request.POST.get("description", "")
        status_id = request.POST.get("status")
        executor_id = request.POST.get("executor")
        label_ids = request.POST.getlist("labels")

        errors = []

        if not name:
            errors.append(constants.ERROR_NAME_REQUIRED)

        if not status_id:
            errors.append(constants.ERROR_STATUS_REQUIRED)

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect(constants.TASKS_URL + "create/")

        task = Task.objects.create(
            name=name,
            description=description,
            status_id=status_id,
            author=request.user,
            executor_id=executor_id if executor_id else None,
        )

        if label_ids:
            task.labels.set(label_ids)

        messages.success(request, constants.SUCCESS_TASK_CREATED)
        return redirect(constants.TASKS_URL)


class TaskUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk)

        if not request.user.is_superuser and task.author != request.user:
            messages.error(request, constants.ERROR_TASK_EDIT_RIGHTS)
            return redirect(constants.TASKS_URL)

        statuses = Status.objects.all()
        users = User.objects.all()
        labels = Label.objects.all()

        context = {
            "task": task,
            "statuses": statuses,
            "users": users,
            "labels": labels,
        }
        return render(request, "tasks/task_update.html", context)

    def post(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk)

        if not request.user.is_superuser and task.author != request.user:
            messages.error(request, constants.ERROR_TASK_EDIT_RIGHTS)
            return redirect(constants.TASKS_URL)

        name = request.POST.get("name")
        description = request.POST.get("description", "")
        status_id = request.POST.get("status")
        executor_id = request.POST.get("executor")
        label_ids = request.POST.getlist("labels")

        errors = []

        if not name:
            errors.append(constants.ERROR_NAME_REQUIRED)

        if not status_id:
            errors.append(constants.ERROR_STATUS_REQUIRED)

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect(f"{constants.TASKS_URL}{pk}/update/")

        task.name = name
        task.description = description
        task.status_id = status_id
        task.executor_id = executor_id if executor_id else None
        task.save()

        task.labels.set(label_ids)

        messages.success(request, constants.SUCCESS_TASK_UPDATED)
        return redirect(constants.TASKS_URL)


class TaskDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk)

        if not request.user.is_superuser and task.author != request.user:
            messages.error(request, constants.ERROR_TASK_DELETE_RIGHTS)
            return redirect(constants.TASKS_URL)

        return render(request, "tasks/task_delete.html", {"task": task})

    def post(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk)

        if not request.user.is_superuser and task.author != request.user:
            messages.error(request, constants.ERROR_TASK_DELETE_RIGHTS)
            return redirect(constants.TASKS_URL)

        task.delete()
        messages.success(request, constants.SUCCESS_TASK_DELETED)
        return redirect(constants.TASKS_URL)
