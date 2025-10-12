from django.contrib.auth.views import LoginView
from .forms import LoginForm, CustomUserCreationForm
from django.urls import reverse_lazy
from .models import User

# from django.db.models import Q
from django.views.generic import CreateView


class CustomLoginView(LoginView):
    """
    A view for Login Page
    """

    template_name = "accounts/login.html"
    form_class = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("task_list")

    # def form_valid(self, form):
    #     username_email = form.cleaned_data.get("username_email")
    #     password = form.cleaned_data.get("password")
    #     user = User.objects.get(Q(username=username_email) | Q(email=username_email))
    #     user = authenticate(self.request, username=user.username, password=password)
    #     if user is not None:
    #         login(self.request, user)
    #         return super(CustomLoginView,self).form_valid(form)
    #     else:
    #         form.add_error(None, "Username or password is incorrect.")
    #         return self.form_invalid(form)


class CustomSignupView(CreateView):
    """
    A view for SignUp Page
    """

    model = User
    form_class = CustomUserCreationForm
    success_url = "/accounts/login"
    template_name = "accounts/signup.html"
    redirect_authenticated_user = True
