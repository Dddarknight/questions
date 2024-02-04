from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from users.views import UserLoginView, UserLogoutView


urlpatterns = [
    path('', RedirectView.as_view(url='/polls/', permanent=True)),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('polls/', include('polls.urls')),
    path('admin/', admin.site.urls),
]
