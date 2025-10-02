from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.TaskListView.as_view(), name="task_list"),
    path("create/", views.TaskCreateView.as_view(), name="create_task"),
    path("update/<int:pk>/", views.TaskUpdateView.as_view(), name="update_task"),
    path("complete/<int:pk>/", views.TaskCompleteView.as_view(), name="complete_task"),
    path("delete/<int:pk>/", views.TaskDeleteView.as_view(), name="delete_task"),
    path("incomplete/<int:pk>/", views.TaskInCompleteView.as_view(), name="incomplete_task"),
    path('api/v1/',include('todo.api.v1.urls')),
]