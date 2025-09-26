from django.urls import path
from . import views

urlpatterns = [
    path("", views.TaskListView.as_view(), name="task_list"),
    path("create/", views.TaskCreateView.as_view(), name="create_task"),
    path("update/<int:pk>/", views.TaskUpdateView.as_view(), name="update_task"),
    path("complete/<int:pk>/", views.TaskCompleteView.as_view(), name="complete_task"),
    path("delete/<int:pk>/", views.TaskDeleteView.as_view(), name="delete_task"),
]