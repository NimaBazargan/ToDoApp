from django.contrib import admin

# Register your models here.
from .models import Task


class TaskAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "complete",
    ]


admin.site.register(Task, TaskAdmin)
