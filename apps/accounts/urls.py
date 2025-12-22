from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # allauth handled separately in config/urls.py
    path('profile/', views.profile, name='profile'),
]
