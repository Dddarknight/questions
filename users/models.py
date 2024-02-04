from django.contrib.auth.models import AbstractUser
from django.urls import reverse_lazy


class User(AbstractUser):
    def get_absolute_url(self):
        return reverse_lazy('users', args=[self.pk])
