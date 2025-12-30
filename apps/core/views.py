from django.shortcuts import render
from apps.images.models import GeneratedImage

def landing(request):
    return render(request, 'core/landing.html')

def dashboard(request):
    history = []
    if request.user.is_authenticated:
        history = GeneratedImage.objects.filter(user=request.user)[:20]
        # Optimize URLs for dashboard thumbnails and high-res viewing
        plan = request.user.userprofile.plan_type
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Dashboard: User {request.user.email} has plan '{plan}'")
        
        for img in history:
            if 'cloudinary.com' in img.image_url and '/upload/' in img.image_url:
                img.thumbnail_url = img.image_url.replace('/upload/', '/upload/w_600,c_scale,q_auto,f_auto/')
                # Generate high-res URL based on plan
                res_limit = "w_4096" if plan == 'agency' else "w_2048"
                img.high_res_url = img.image_url.replace('/upload/', f'/upload/{res_limit},c_scale,q_auto:best/')
                logger.info(f"Dashboard: Generated high-res URL with {res_limit} for image {img.id}")
            else:
                img.thumbnail_url = img.image_url
                img.high_res_url = img.image_url
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
