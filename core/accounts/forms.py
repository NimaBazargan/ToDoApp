from django import forms
from .models import User

# from django.contrib.auth.models import User
# from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm

# class CustomAuthenticationForm(forms.ModelForm):
#     username_email = forms.CharField(label='Username or Email', max_length=255)

#     class Meta:
#         model = User
#         fields = ['username_email','password',]

#     def __init__(self, *args, **kwargs):
#         self.request = kwargs.pop('request', None)  # حذف پارامتر 'request' از kwargs
#         super().__init__(*args, **kwargs)

#     def clean_username_email(self):
#         username_email = self.cleaned_data.get('username_email')
#         users = User.objects.filter(Q(username=username_email) | Q(email=username_email))
#         if not users.exists():
#             raise forms.ValidationError("The user doesn't exist or Password is incorrect.")
#         return username_email

# def get_user(self):
#     username_email = self.cleaned_data.get('username_email')
#     user = User.objects.filter(Q(username=username_email) | Q(email=username_email)).first()
#     return user  # Return the user instance


class CustomUserCreationForm(UserCreationForm):
    """
    This is a form for signup
    """

    class Meta:
        model = User
        fields = [
            "email",
            "password1",
            "password2",
        ]


class LoginForm(forms.Form):
    """
    This is a form for login
    """

    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)  # حذف پارامتر 'request' از kwargs
        super().__init__(*args, **kwargs)

    def get_user(self):
        email = self.cleaned_data.get("email")
        user = User.objects.filter(email=email).first()
        return user  # Return the user instance
