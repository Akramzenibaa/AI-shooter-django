from django.urls import path
from . import views, webhooks

app_name = 'accounts'

urlpatterns = [
    # allauth handled separately in config/urls.py
    path('profile/', views.profile, name='profile'),
    path('webhook/polar/', webhooks.polar_webhook, name='polar_webhook'),
    path('checkout/<str:product_id>/', views.create_checkout, name='create_checkout'),
]
