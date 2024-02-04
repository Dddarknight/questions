from .forms import LoginForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from .mixins import MessageLogOutMixin


LOGGED_IN_MESSAGE = "Вы залогинены"


class UserLoginView(SuccessMessageMixin, LoginView):
    template_name = 'login.html'
    form_class = LoginForm
    success_message = LOGGED_IN_MESSAGE


class UserLogoutView(MessageLogOutMixin, LogoutView):
    pass
