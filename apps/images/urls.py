from django.urls import path
from . import views

app_name = 'images'

urlpatterns = [
    path('generate/', views.generate_image, name='generate'),
]
