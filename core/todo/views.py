from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Task
from .forms import TaskForm
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

class TaskListView(LoginRequiredMixin,ListView):
    context_object_name = "tasks"
    template_name = "todo/list_task.html"

    def get_queryset(self):
        tasks = Task.objects.filter(user=self.request.user)
        return tasks
    
class TaskCreateView(LoginRequiredMixin,CreateView):
    model = Task
    form_class = TaskForm
    success_url = '/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreateView,self).form_valid(form)
    
class TaskUpdateView(LoginRequiredMixin,UpdateView):
    model = Task
    form_class = TaskForm
    success_url = '/'
    template_name = "todo/update_task.html"

class TaskCompleteView(LoginRequiredMixin,View):
    model = Task
    success_url = '/'

    def get(self, request, *args, **kwargs):
        object = Task.objects.get(id=kwargs.get("pk"))
        object.complete = True
        object.save()
        return redirect(self.success_url)
    
class TaskDeleteView(LoginRequiredMixin,DeleteView):
    model = Task
    success_url = '/'

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect(self.success_url)




