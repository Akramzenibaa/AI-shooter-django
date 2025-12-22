from django.shortcuts import render
from apps.images.models import GeneratedImage

def landing(request):
    return render(request, 'core/landing.html')

def dashboard(request):
    history = []
    if request.user.is_authenticated:
        history = GeneratedImage.objects.filter(user=request.user)[:20]
    return render(request, 'core/dashboard.html', {'history': history})
