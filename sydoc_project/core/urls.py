from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', login_required(views.profile), name='profile'),
    path('profile/edit/', login_required(views.edit_profile), name='edit_profile'),
]
