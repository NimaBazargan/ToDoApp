from celery import shared_task
from todo.models import Task


@shared_task
def deleteTask():
    tasks = Task.objects.filter(complete=True)
    for task in tasks:
        task.delete()
