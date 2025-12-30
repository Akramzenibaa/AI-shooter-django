from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .tasks import generate_images_task
from .models import GeneratedImage
import logging

logger = logging.getLogger(__name__)

@login_required
def generate_image(request):
    if request.method == 'POST':
        try:
            image_file = request.FILES.get('image')
            count = int(request.POST.get('count', 4))
            mode = request.POST.get('mode', 'creative')
            user_prompt = request.POST.get('user_prompt', '')
            
            user_profile = request.user.userprofile
            if user_profile.credits < count:
                return JsonResponse({'error': 'Not enough credits'}, status=402)
            
            # Read image data once to pass to background task
            image_data = image_file.read()
            
            # 1. Deduct credits immediately to prevent double-spending
            user_profile.credits -= count
            user_profile.save()
            logger.info(f"Credits deducted. New balance: {user_profile.credits}")
            
            # 2. Trigger background task
            task = generate_images_task(
                user_id=request.user.id,
                image_data=image_data,
                count=count,
                mode=mode,
                user_prompt=user_prompt,
                plan=user_profile.plan_type
            )
            
            return JsonResponse({
                'status': 'queued',
                'task_id': task.id,
                'new_credits': user_profile.credits
            })
            
        except Exception as e:
            logger.error(f"Error triggering task: {str(e)}")
            return JsonResponse({'error': f'Server Error: {str(e)}'}, status=500)
            
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def task_status(request, task_id):
    """
    Check the status of a specific background task.
    """
    # This requires reaching into Huey's result store
    # Given we use django-huey, we can use the result() method
    from django_huey import get_queue
    queue = get_queue('default')
    result = queue.result(task_id)
    
    if result is None:
        return JsonResponse({'status': 'processing'})
    
    if isinstance(result, dict) and result.get('status') == 'error':
        return JsonResponse({
            'status': 'error',
            'message': result.get('message', 'Unknown error in background task')
        })
        
    # Prepare high-res versions for the frontend
    urls = result.get('urls', [])
    plan = request.user.userprofile.plan_type
    res_limit = "w_4096" if plan == 'agency' else "w_2048"
    
    logger.info(f"Task status: User plan is '{plan}', using resolution limit: {res_limit}")
    
    high_res_urls = []
    for url in urls:
        if 'cloudinary.com' in url and '/upload/' in url:
            high_res_url = url.replace('/upload/', f'/upload/{res_limit},c_scale,q_auto:best,f_png/')
            high_res_urls.append(high_res_url)
            logger.info(f"Generated high-res URL: {high_res_url}")
        else:
            high_res_urls.append(url)

    return JsonResponse({
        'status': 'success',
        'urls': urls,
        'high_res_urls': high_res_urls
    })


