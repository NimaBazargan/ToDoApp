from django_filters import rest_framework as filters
from todo.models import Task


class TaskFilter(filters.FilterSet):

    class Meta:
        model = Task
        fields = ["user", "title"]
