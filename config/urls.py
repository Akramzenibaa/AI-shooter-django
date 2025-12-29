from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.accounts import webhooks

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')), # Social login
    path('user/', include('apps.accounts.urls')), # Profiles
    path('images/', include('apps.images.urls')), # Image gen
    path('', include('apps.core.urls')), # Main dashboard
    # Specific webhook path to match user configuration
    path('payments/webhook/', webhooks.polar_webhook, name='polar_webhook_payments'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Serve media files in production (required for Coolify/Docker without Nginx)
    from django.views.static import serve
    from django.urls import re_path
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
