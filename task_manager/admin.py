from django.contrib import admin

from .models import Label, Status, Task


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    ordering = ("id",)


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    ordering = ("id",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "status", "author", "executor", "created_at")
    list_display_links = ("id", "name")
    list_filter = ("status", "author", "executor", "labels")
    search_fields = ("name", "description")
    filter_horizontal = ("labels",)  # Удобный виджет для выбора меток
    readonly_fields = ("created_at",)
    fieldsets = (
        (
            "Основная информация",
            {"fields": ("name", "description", "created_at")},
        ),
        ("Связи", {"fields": ("status", "author", "executor", "labels")}),
    )
    ordering = ("-created_at",)
