from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .. import constants
from ..models import Status

STATUS_CREATE_TEMPLATE = "statuses/status_create.html"
STATUS_UPDATE_TEMPLATE = "statuses/status_update.html"


class StatusListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        statuses = Status.objects.all().order_by("id")
        return render(request, "statuses/statuses.html", {"statuses": statuses})


class StatusCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, STATUS_CREATE_TEMPLATE)

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")

        if not name:
            messages.error(request, constants.ERROR_NAME_REQUIRED)
            return render(request, STATUS_CREATE_TEMPLATE)

        if Status.objects.filter(name=name).exists():
            messages.error(request, constants.ERROR_STATUS_EXISTS)
            return render(request, STATUS_CREATE_TEMPLATE)

        Status.objects.create(name=name)
        messages.success(request, constants.SUCCESS_STATUS_CREATED)
        return redirect(constants.STATUSES_URL)


class StatusUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        status = get_object_or_404(Status, pk=pk)
        return render(request, STATUS_UPDATE_TEMPLATE, {"status": status})

    def post(self, request, pk, *args, **kwargs):
        status = get_object_or_404(Status, pk=pk)
        name = request.POST.get("name")

        if not name:
            messages.error(request, constants.ERROR_NAME_REQUIRED)
            return render(request, STATUS_UPDATE_TEMPLATE, {"status": status})

        if name != status.name and Status.objects.filter(name=name).exists():
            messages.error(request, constants.ERROR_STATUS_EXISTS)
            return render(request, STATUS_UPDATE_TEMPLATE, {"status": status})

        status.name = name
        status.save()

        messages.success(request, constants.SUCCESS_STATUS_UPDATED)
        return redirect(constants.STATUSES_URL)


class StatusDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        status = get_object_or_404(Status, pk=pk)

        return render(request, "statuses/status_delete.html",
                    {"status": status})

    def post(self, request, pk, *args, **kwargs):
        status = get_object_or_404(Status, pk=pk)

        if status.tasks.exists():
            messages.error(request, constants.ERROR_CANNOT_DELETE_STATUS)
            return redirect(constants.STATUSES_URL)

        status.delete()
        messages.success(request, constants.SUCCESS_STATUS_DELETED)
        return redirect(constants.STATUSES_URL)
