from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .. import constants
from ..models import Label

LABEL_CREATE_TEMPLATE = "labels/label_create.html"
LABEL_UPDATE_TEMPLATE = "labels/label_update.html"


class LabelListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        labels = Label.objects.all().order_by("id")
        return render(request, "labels/labels.html", {"labels": labels})


class LabelCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, LABEL_CREATE_TEMPLATE)

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")

        if not name:
            messages.error(request, constants.ERROR_NAME_REQUIRED)
            return render(request, LABEL_CREATE_TEMPLATE)

        if Label.objects.filter(name=name).exists():
            messages.error(request, constants.ERROR_LABEL_EXISTS)
            return render(request, LABEL_CREATE_TEMPLATE)

        Label.objects.create(name=name)
        messages.success(request, constants.SUCCESS_LABEL_CREATED)
        return redirect(constants.LABELS_URL)


class LabelUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        label = get_object_or_404(Label, pk=pk)
        return render(request, LABEL_UPDATE_TEMPLATE, {"label": label})

    def post(self, request, pk, *args, **kwargs):
        label = get_object_or_404(Label, pk=pk)
        name = request.POST.get("name")

        if not name:
            messages.error(request, constants.ERROR_NAME_REQUIRED)
            return render(request, LABEL_UPDATE_TEMPLATE, {"label": label})

        if name != label.name and Label.objects.filter(name=name).exists():
            messages.error(request, constants.ERROR_LABEL_EXISTS)
            return render(request, LABEL_UPDATE_TEMPLATE, {"label": label})

        label.name = name
        label.save()

        messages.success(request, constants.SUCCESS_LABEL_UPDATED)
        return redirect(constants.LABELS_URL)


class LabelDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        label = get_object_or_404(Label, pk=pk)

        if label.tasks.exists():
            messages.error(request, constants.ERROR_CANNOT_DELETE_LABEL)
            return redirect(constants.LABELS_URL)

        return render(request, "labels/label_delete.html", {"label": label})

    def post(self, request, pk, *args, **kwargs):
        label = get_object_or_404(Label, pk=pk)

        if label.tasks.exists():
            messages.error(request, constants.ERROR_CANNOT_DELETE_LABEL)
            return redirect(constants.LABELS_URL)

        label.delete()
        messages.success(request, constants.SUCCESS_LABEL_DELETED)
        return redirect(constants.LABELS_URL)
