from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from .serializers import (
    RegistrationSerializer,
    CustomAuthTokenSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer,
    ProfileSerializer,
    ActivationResendSerializer,
    ResetPasswordSerializer,
    ResetConfirmSerializer,
)
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from mail_templated import EmailMessage
from ..utils import EmailThread
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.views import ObtainAuthToken, APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from accounts.models import Profile
import jwt
from django.conf import settings
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError
from .permissions import AllowUnauthenticatedUser
from rest_framework.exceptions import PermissionDenied
from datetime import datetime, timedelta

User = get_user_model()


class RegistrationApiView(GenericAPIView):
    """
    Register a user and sending a user vertification link via email
    """

    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        email = serializer.validated_data["email"]
        data = {
            "email": email,
        }
        user = get_object_or_404(User, email=email)
        token = self.get_tokens_for_user(user)
        email_obj = EmailMessage(
            "email/activation.tpl",
            {"token": token},
            "nima.kazemzadeh.bazargan@gmail.com",
            to=[email],
        )
        EmailThread(email_obj).start()
        return Response(data, status=status.HTTP_201_CREATED)

    def get_tokens_for_user(self, user):
        """
        Creating a jwt for each user
        """
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


class CustomAuthToken(ObtainAuthToken):
    """
    Logging in and getting a token
    """

    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user_id": user.pk, "email": user.email})


class CustomDiscardAuthToken(APIView):
    """
    Clear token
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Getting jwt
    """

    serializer_class = CustomTokenObtainPairSerializer


class ChangePasswordApiView(GenericAPIView):
    """
    Change password and check new password
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def put(self, request):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(
                {"detail": "password changed successfully"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileApiView(RetrieveUpdateAPIView):
    """
    Getting profile and updating it
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, user=self.request.user)
        return obj


class ActivationApiView(APIView):
    """
    Getting the emailed link and verifying the user
    """

    def get(self, request, token):
        try:
            token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = token.get("user_id")
        except ExpiredSignatureError:
            return Response(
                {"detail": "token has been expired"}, status=status.HTTP_400_BAD_REQUEST
            )
        except InvalidSignatureError:
            return Response(
                {"detail": "token is not valid"}, status=status.HTTP_400_BAD_REQUEST
            )
        user_obj = User.objects.get(id=user_id)
        if user_obj.is_verified:
            return Response({"detail": "your account has already been verified"})
        user_obj.is_verified = True
        user_obj.save()
        return Response(
            {"detail": "your account has been verified and activated successfully"}
        )


class ActivationResendApiView(GenericAPIView):
    serializer_class = ActivationResendSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = serializer.validated_data["user"]
        token = self.get_tokens_for_user(user_obj)
        email_obj = EmailMessage(
            "email/activation.tpl",
            {"token": token},
            "nima.kazemzadeh.bazargan@gmail.com",
            to=[user_obj.email],
        )
        EmailThread(email_obj).start()
        return Response(
            {"detail": "user activation resend successfully"}, status=status.HTTP_200_OK
        )

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


class ResetPasswordApiView(GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowUnauthenticatedUser]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = serializer.validated_data["user"]
        token = self.get_tokens_for_user(user_obj)
        email_obj = EmailMessage(
            "email/reset.tpl",
            {"token": token},
            "nima.kazemzadeh.bazargan@gmail.com",
            to=[user_obj.email],
        )
        EmailThread(email_obj).start()
        return Response(
            {
                "detail": "you can reset your password via the link which sent to your email"
            },
            status=status.HTTP_200_OK,
        )

    def get_tokens_for_user(self, user):
        exp = datetime.now() + timedelta(minutes=1)
        token = {
            "user_id": user.id,
            "exp": exp,
        }
        return jwt.encode(token, settings.SECRET_KEY, algorithm="HS256")

    def handle_exception(self, exc):
        if isinstance(exc, PermissionDenied):
            return Response(
                {"detail": "You should be logged out to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().handle_exception(exc)


class ResetConfirmApiView(GenericAPIView):
    serializer_class = ResetConfirmSerializer
    permission_classes = [AllowUnauthenticatedUser]

    def put(self, request, token):
        try:
            token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = token.get("user_id")
        except ExpiredSignatureError:
            return Response(
                {"detail": "token has been expired"}, status=status.HTTP_400_BAD_REQUEST
            )
        except InvalidSignatureError:
            return Response(
                {"detail": "token is not valid"}, status=status.HTTP_400_BAD_REQUEST
            )
        user_obj = User.objects.get(id=user_id)
        self.object = user_obj
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(
                {"detail": "password changed successfully"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def handle_exception(self, exc):
        if isinstance(exc, PermissionDenied):
            return Response(
                {"detail": "You should be logged out to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().handle_exception(exc)
