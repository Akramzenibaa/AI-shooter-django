from django.urls import path
from . import views

app_name = 'images'

urlpatterns = [
    path('generate/', views.generate_image, name='generate'),
    path('status/<str:task_id>/', views.task_status, name='task_status'),
]
