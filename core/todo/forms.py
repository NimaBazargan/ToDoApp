from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    """
    This is a form for Task model
    """

    class Meta:
        model = Task
        fields = ['title',]