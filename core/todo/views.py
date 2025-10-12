from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Task
from .forms import TaskForm
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import Profile
from django.core.exceptions import PermissionDenied


class TaskListView(LoginRequiredMixin, ListView):
    """
    Getting a list of tasks
    """

    context_object_name = "tasks"
    template_name = "todo/list_task.html"

    def get_queryset(self):
        profile = Profile.objects.get(user=self.request.user)
        tasks = Task.objects.filter(user=profile)
        return tasks


class TaskCreateView(LoginRequiredMixin, CreateView):
    """
    Creating new task
    """

    model = Task
    form_class = TaskForm
    success_url = "/"

    def form_valid(self, form):
        profile = Profile.objects.get(user=self.request.user)
        form.instance.user = profile
        return super(TaskCreateView, self).form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    """
    Editing a task
    """

    model = Task
    form_class = TaskForm
    success_url = "/"
    template_name = "todo/update_task.html"

    def get_object(self, queryset=None):
        obj = super(TaskUpdateView, self).get_object(queryset)
        if obj.user.user != self.request.user:
            raise PermissionDenied
        return obj


class TaskCompleteView(LoginRequiredMixin, View):
    """
    Changing task complete to True
    """

    model = Task
    success_url = "/"

    def get(self, request, *args, **kwargs):
        object = Task.objects.get(id=kwargs.get("pk"))
        if object.user.user == request.user:
            object.complete = True
            object.save()
        return redirect(self.success_url)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    """
    Deleting a task
    """

    model = Task
    success_url = "/"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.user.user == self.request.user:
            self.object.delete()
        return redirect(self.success_url)


class TaskInCompleteView(LoginRequiredMixin, View):
    """
    Changing task complete to False
    """

    model = Task
    success_url = "/"

    def get(self, request, *args, **kwargs):
        object = Task.objects.get(id=kwargs.get("pk"))
        if object.user.user == request.user:
            object.complete = False
            object.save()
        return redirect(self.success_url)
