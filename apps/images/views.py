from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .services import generate_campaign_images
from .models import GeneratedImage
import os

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
            
            # Call Gemini service
            results = generate_campaign_images(
                image_file, 
                count=count, 
                mode=mode, 
                user_prompt=user_prompt,
                plan=user_profile.plan_type
            )
            
            if not results:
                # If service returned empty, check if it's likely a quota issue
                return JsonResponse({
                    'error': 'Generation failed. This is usually due to AI API rate limits (Free Tier). Please try again in 1 minute.'
                }, status=500)

            urls = [res['url'] for res in results]
                
            # Success! Deduct credits and save metadata
            user_profile.credits -= count
            user_profile.save()
            
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Credits deducted. New balance: {user_profile.credits}")
            
            for res in results:
                img_obj = GeneratedImage.objects.create(
                    user=request.user,
                    original_image=image_file,
                    image_url=res['url'],
                    count=count
                )
                logger.info(f"GeneratedImage saved to DB: ID {img_obj.id}, URL {res['url']}")
                
            return JsonResponse({
                'status': 'success',
                'urls': urls,
                'new_credits': user_profile.credits
            })
        except Exception as e:
            return JsonResponse({'error': f'Server Error: {str(e)}'}, status=500)
            
    return JsonResponse({'error': 'Invalid request'}, status=400)


