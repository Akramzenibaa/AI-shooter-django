from django_huey import db_task
from .services import generate_campaign_images
from .models import GeneratedImage
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

@db_task()
def generate_images_task(user_id, image_data, count, mode, user_prompt, plan):
    """
    Background task to generate images using Gemini and upload to Cloudinary.
    """
    try:
        user = User.objects.get(id=user_id)
        user_profile = user.userprofile
        
        logger.info(f"Starting background generation task for user {user.email}")
        
        # Call the existing service
        # Note: image_data should be bytes
        from io import BytesIO
        image_file = BytesIO(image_data)
        image_file.name = "input_image.png" # Dummy name for Cloudinary
        
        results = generate_campaign_images(
            image_file,
            count=count,
            mode=mode,
            user_prompt=user_prompt,
            plan=plan
        )
        
        if not results:
            logger.error("Background generation failed: No results returned")
            return {'status': 'error', 'message': 'Generation failed'}

        # Save to database
        created_count = 0
        saved_urls = []
        for res in results:
            img_obj = GeneratedImage.objects.create(
                user=user,
                original_image=None, # We don't have the original File object easily here, but we can skip it for now or store the bytes if needed
                image_url=res['url'],
                count=count
            )
            saved_urls.append(res['url'])
            created_count += 1
            logger.info(f"Background task: GeneratedImage saved ID {img_obj.id}")

        return {
            'status': 'success',
            'urls': saved_urls,
            'new_credits': user_profile.credits # Credits were already deducted in the view
        }

    except Exception as e:
        logger.error(f"Background task error: {str(e)}")
        return {'status': 'error', 'message': str(e)}
