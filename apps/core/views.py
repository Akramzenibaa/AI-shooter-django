from django.shortcuts import render
from apps.images.models import GeneratedImage

def landing(request):
    return render(request, 'core/landing.html')

def dashboard(request):
    history = []
    if request.user.is_authenticated:
        history = GeneratedImage.objects.filter(user=request.user)[:20]
        # Optimize URLs for dashboard thumbnails to prevent scroll lag
        for img in history:
            if 'cloudinary.com' in img.image_url and '/upload/' in img.image_url:
                img.thumbnail_url = img.image_url.replace('/upload/', '/upload/w_400,c_scale,q_auto,f_auto/')
            else:
                img.thumbnail_url = img.image_url
    return render(request, 'core/dashboard.html', {'history': history})

def about(request):
    return render(request, 'core/about.html')

def privacy(request):
    return render(request, 'core/privacy.html')

def terms(request):
    return render(request, 'core/terms.html')

def blog(request):
    return render(request, 'core/blog.html')

def pricing(request):
    return render(request, 'core/pricing.html')
