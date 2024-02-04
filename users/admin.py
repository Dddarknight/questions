from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from users.models import User as User_


class UserAdmin(BaseUserAdmin):
    pass


admin.site.register(User_, UserAdmin)
