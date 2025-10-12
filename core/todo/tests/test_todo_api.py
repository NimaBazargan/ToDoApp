from rest_framework.test import APIClient
import pytest
from django.urls import reverse
from accounts.models import User, Profile
from todo.models import Task

@pytest.fixture
def api_client():
    client = APIClient()
    return client

@pytest.fixture
def common_user():
    user = User.objects.create_user(email='test@test.com',password='a/@123456')
    return user

@pytest.fixture
def common_user_invalid():
    user = User.objects.create_user(email='user@test.com',password='a/@123456')
    return user

@pytest.fixture
def common_profile(common_user):
    user = common_user
    profile = Profile.objects.create(user=user,first_name='test_first_name',last_name='test_last_name',description='test')
    return profile

@pytest.fixture
def common_task(common_profile):
    user = common_profile
    task = Task.objects.create(user=user,title='test')
    return task

@pytest.mark.django_db
class TestTodoApi:

    def test_get_tasks_response_200_status(self,api_client):
        url = reverse('api-v1:task-list')
        response = api_client.get(url)
        assert response.status_code == 200

    def test_create_task_response_401_status(self,api_client):
        url = reverse('api-v1:task-list')
        data = {
            'title' : 'test'
        }
        response = api_client.post(url,data)
        assert response.status_code == 401

    def test_create_task_response_400_status(self,api_client,common_user):
        url = reverse('api-v1:task-list')
        data = {
        }
        user = common_user
        api_client.force_authenticate(user=user)
        response = api_client.post(url,data)
        assert response.status_code == 400

    def test_create_task_response_201_status(self,api_client,common_user):
        url = reverse('api-v1:task-list')
        data = {
            'title' : 'test'
        }
        user = common_user
        api_client.force_authenticate(user=user)
        response = api_client.post(url,data)
        assert response.status_code == 201
        assert Task.objects.filter(title='test').exists()

    def test_get_task_response_200_status(self,api_client,common_task):
        task = common_task
        url = reverse('api-v1:task-detail', kwargs={'pk': task.id})
        response = api_client.get(url)
        assert response.status_code == 200

    def test_update_task_response_401_status(self,api_client,common_task):
        task = common_task
        url = reverse('api-v1:task-detail', kwargs={'pk': task.id})
        data = {
            'complete': True
        }
        response = api_client.put(url,data)
        response1 = api_client.patch(url,data)
        assert (response.status_code == 401 and response1.status_code == 401)

    def test_update_task_response_403_status(self,api_client,common_user_invalid,common_task):
        task = common_task
        url = reverse('api-v1:task-detail', kwargs={'pk': task.id})
        data = {
            'complete': True
        }
        user = common_user_invalid
        api_client.force_authenticate(user=user)
        response = api_client.put(url,data)
        response1 = api_client.patch(url,data)
        assert (response.status_code == 403 and response1.status_code == 403)

    def test_put_task_response_400_status(self,api_client,common_user,common_task):
        task = common_task
        url = reverse('api-v1:task-detail', kwargs={'pk': task.id})
        data ={
        }
        user = common_user
        api_client.force_authenticate(user=user)
        response = api_client.put(url,data)
        assert response.status_code == 400

    def test_put_task_response_200_status(self,api_client,common_user,common_task):
        task = common_task
        url = reverse('api-v1:task-detail', kwargs={'pk': task.id})
        data ={
            'title' : 'test',
            'complete': True
        }
        user = common_user
        api_client.force_authenticate(user=user)
        response = api_client.put(url,data)
        assert response.status_code == 200

    def test_patch_task_response_200_status(self,api_client,common_user,common_task):
        task = common_task
        url = reverse('api-v1:task-detail', kwargs={'pk': task.id})
        data ={
            'complete': True
        }
        user = common_user
        api_client.force_authenticate(user=user)
        response = api_client.patch(url,data)
        assert response.status_code == 200

    def test_delete_task_response_401_status(self,api_client,common_task):
        task = common_task
        url = reverse('api-v1:task-detail', kwargs={'pk': task.id})
        response = api_client.delete(url)
        assert response.status_code == 401

    def test_delete_task_response_403_status(self,api_client,common_user_invalid,common_task):
        task = common_task
        url = reverse('api-v1:task-detail', kwargs={'pk': task.id})
        user = common_user_invalid
        api_client.force_authenticate(user=user)
        response = api_client.delete(url)
        assert response.status_code == 403

    def test_delete_task_response_204_status(self,api_client,common_user,common_task):
        task = common_task
        url = reverse('api-v1:task-detail', kwargs={'pk': task.id})
        user = common_user
        api_client.force_authenticate(user=user)
        response = api_client.delete(url)
        assert response.status_code == 204

    




