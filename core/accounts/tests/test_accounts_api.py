from rest_framework.test import APIClient
import pytest
from django.urls import reverse
from accounts.models import User
from datetime import datetime, timedelta
import jwt
from django.conf import settings


@pytest.fixture
def api_client():
    client = APIClient()
    return client


@pytest.fixture
def common_user():
    user = User.objects.create_user(
        email="test@test.com", password="a/@123456", is_verified=True
    )
    return user


@pytest.fixture
def common_user_invalid():
    user = User.objects.create_user(email="user@test.com", password="a/@123456")
    return user


@pytest.fixture
def get_tokens_for_user(common_user):
    user = common_user
    exp = datetime.now() + timedelta(minutes=1)
    token = {
        "user_id": user.id,
        "exp": exp,
    }
    return jwt.encode(token, settings.SECRET_KEY, algorithm="HS256")


@pytest.mark.django_db
class TestRegistrationAndActivationApi:

    def test_registration_response_400_status(self, api_client):
        url = reverse("accounts:api-v1:registration")
        data = {}
        response = api_client.post(url, data)
        assert response.status_code == 400

    def test_exist_email_response_400_status(self, api_client, common_user):
        url = reverse("accounts:api-v1:registration")
        data = {
            "email": "test@test.com",
            "password": "string123",
            "password_confirm": "string123",
        }
        response = api_client.post(url, data)
        assert response.status_code == 400

    def test_response_current_status(
        self, api_client, common_user, get_tokens_for_user
    ):
        url = reverse("accounts:api-v1:registration")
        data = {
            "email": "user@example.com",
            "password": "string123",
            "password_confirm": "string123",
        }
        response = api_client.post(url, data)
        assert response.status_code == 201
        token = get_tokens_for_user
        url = reverse("accounts:api-v1:activation", kwargs={"token": token})
        response = api_client.get(url)
        assert response.status_code == 200

    def test_resend_400_status(self, api_client, common_user):
        url = reverse("accounts:api-v1:activation-resend")
        data = {"email": "user@test.com"}
        response = api_client.post(url, data)
        assert response.status_code == 400

    def test_resend_200_status(self, api_client, common_user):
        url = reverse("accounts:api-v1:activation-resend")
        data = {"email": "test@test.com"}
        response = api_client.post(url, data)
        assert response.status_code == 200


@pytest.mark.django_db
class TestTokenApi:

    def test_login_response_400_status(self, api_client):
        url = reverse("accounts:api-v1:token-login")
        data = {}
        response = api_client.post(url, data)
        assert response.status_code == 400

    def test_login_not_exist_email_response_400_status(self, api_client, common_user):
        url = reverse("accounts:api-v1:token-login")
        data = {
            "email": "user@example.com",
            "password": "string123",
        }
        response = api_client.post(url, data)
        assert response.status_code == 400

    def test_response_correct_status(self, api_client, common_user):
        url = reverse("accounts:api-v1:token-login")
        data = {
            "email": "test@test.com",
            "password": "a/@123456",
        }
        response = api_client.post(url, data)
        assert response.status_code == 200
        url = reverse("accounts:api-v1:token-logout")
        user = common_user
        api_client.force_authenticate(user=user)
        response = api_client.post(url)
        assert response.status_code == 204

    def test_logout_response_401_status(self, api_client):
        url = reverse("accounts:api-v1:token-logout")
        response = api_client.post(url)
        assert response.status_code == 401


@pytest.mark.django_db
class TestJWTApi:

    def test_create_response_401_status(self, api_client, common_user):
        url = reverse("accounts:api-v1:jwt-create")
        data = {"email": "user@example.com", "password": "a/@123456"}
        response = api_client.post(url, data)
        assert response.status_code == 401

    def test_create_response_400_status(self, api_client, common_user_invalid):
        url = reverse("accounts:api-v1:jwt-create")
        data = {"email": "user@test.com", "password": "a/@123456"}
        response = api_client.post(url, data)
        assert response.status_code == 400

    def test_response_200_status(self, api_client, common_user):
        url = reverse("accounts:api-v1:jwt-create")
        data = {"email": "test@test.com", "password": "a/@123456"}
        response = api_client.post(url, data)
        assert response.status_code == 200
        url = reverse("accounts:api-v1:jwt-verify")
        refresh = response.data["refresh"]
        access = response.data["access"]
        data = {"token": refresh}
        response = api_client.post(url, data)
        assert response.status_code == 200
        data = {"token": access}
        response = api_client.post(url, data)
        assert response.status_code == 200
        url = reverse("accounts:api-v1:jwt-refresh")
        data = {"refresh": refresh}
        response = api_client.post(url, data)
        assert response.status_code == 200
        url = reverse("accounts:api-v1:jwt-verify")
        access = response.data["access"]
        data = {"token": access}
        response = api_client.post(url, data)
        assert response.status_code == 200

    def test_refresh_response_401_status(self, api_client):
        url = reverse("accounts:api-v1:jwt-refresh")
        data = {"refresh": "test"}
        response = api_client.post(url, data)
        assert response.status_code == 401

    def test_refresh_response_400_status(self, api_client):
        url = reverse("accounts:api-v1:jwt-refresh")
        data = {}
        response = api_client.post(url, data)
        assert response.status_code == 400

    def test_verify_response_401_status(self, api_client):
        url = reverse("accounts:api-v1:jwt-verify")
        data = {"token": "test"}
        response = api_client.post(url, data)
        assert response.status_code == 401

    def test_verify_response_400_status(self, api_client):
        url = reverse("accounts:api-v1:jwt-verify")
        data = {}
        response = api_client.post(url, data)
        assert response.status_code == 400


@pytest.mark.django_db
class TestChangePasswordApi:

    def test_response_401_status(self, api_client):
        url = reverse("accounts:api-v1:change-password")
        data = {
            "old_password": "a/@123456",
            "new_password": "string123",
            "new_password_confirm": "string123",
        }
        response = api_client.put(url, data)
        assert response.status_code == 401

    def test_response_405_status(self, api_client, common_user):
        url = reverse("accounts:api-v1:change-password")
        data = {
            "old_password": "a/@12345",
            "new_password": "string123",
            "new_password_confirm": "string1234",
        }
        user = common_user
        api_client.force_authenticate(user=user)
        response = api_client.put(url, data)
        assert response.status_code == 400

    def test_response_200_status(self, api_client, common_user):
        url = reverse("accounts:api-v1:change-password")
        data = {
            "old_password": "a/@123456",
            "new_password": "a/@1234567",
            "new_password_confirm": "a/@1234567",
        }
        user = common_user
        api_client.force_authenticate(user=user)
        response = api_client.put(url, data)
        assert response.status_code == 200


@pytest.mark.django_db
class TestProfileApi:

    def test_response_401_status(self, api_client):
        url = reverse("accounts:api-v1:profile")
        response = api_client.get(url)
        assert response.status_code == 401

    def test_response_200_status(self, api_client, common_user):
        url = reverse("accounts:api-v1:profile")
        user = common_user
        api_client.force_authenticate(user=user)
        response = api_client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestResetApi:

    def test_reset_403_status(self, api_client, common_user):
        url = reverse("accounts:api-v1:reset-password")
        data = {"email": "test@test.com"}
        user = common_user
        api_client.force_authenticate(user=user)
        response = api_client.post(url, data)
        assert response.status_code == 403

    def test_reset_400_status(self, api_client, common_user):
        url = reverse("accounts:api-v1:reset-password")
        data = {"email": "user@test.com"}
        response = api_client.post(url, data)
        assert response.status_code == 400

    def test_200_status(self, api_client, common_user, get_tokens_for_user):
        url = reverse("accounts:api-v1:reset-password")
        data = {"email": "test@test.com"}
        response = api_client.post(url, data)
        assert response.status_code == 200
        token = get_tokens_for_user
        url = reverse("accounts:api-v1:reset-password-confirm", kwargs={"token": token})
        data = {"new_password": "string123", "new_password_confirm": "string123"}
        response = api_client.put(url, data)
        assert response.status_code == 200

    def test_confirm_400_status(self, api_client, common_user, get_tokens_for_user):
        url = reverse("accounts:api-v1:reset-password")
        data = {"email": "test@test.com"}
        response = api_client.post(url, data)
        assert response.status_code == 200
        token = get_tokens_for_user
        url = reverse("accounts:api-v1:reset-password-confirm", kwargs={"token": token})
        data = {"new_password": "string123", "new_password_confirm": "string1234"}
        response = api_client.put(url, data)
        assert response.status_code == 400
