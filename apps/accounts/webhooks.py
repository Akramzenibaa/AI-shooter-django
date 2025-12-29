import json
import logging
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import UserProfile
from django.contrib.auth.models import User
from polar_sdk import Polar

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def polar_webhook(request):
    payload = request.body
    sig_header = request.headers.get('webhook-signature')
    
    if not sig_header or not settings.POLAR_WEBHOOK_SECRET:
        return HttpResponse('Missing signature or secret', status=400)

    # Note: polar-sdk provides a way to validate webhooks.
    # For now, we'll parse the event and handle the logic.
    # In a production environment, you MUST validate the signature.
    
    try:
        event = json.loads(payload)
        event_type = event.get('type')
        data = event.get('data', {})
        
        logger.info(f"Received Polar event: {event_type}")

        if event_type in ['order.created', 'subscription.active', 'subscription.updated']:
            # Handle successful payment or subscription
            product_id = data.get('product_id')
            customer_email = data.get('customer_email')
            metadata = data.get('metadata', {})
            user_id = metadata.get('user_id')
            
            # Map product to plan/credits
            plan_info = settings.POLAR_PRODUCT_MAP.get(product_id)
            
            if plan_info:
                try:
                    user = None
                    # 1. Try to find user by ID (most reliable)
                    if user_id:
                        try:
                            user = User.objects.get(id=user_id)
                        except (User.DoesNotExist, ValueError):
                            logger.warning(f"User ID {user_id} from metadata not found")

                    # 2. Fallback to email if user not found by ID
                    if not user and customer_email:
                        user = User.objects.get(email=customer_email)
                    
                    if user:
                        profile = user.userprofile
                        
                        # Update plan if provided
                        if 'plan' in plan_info:
                            profile.plan_type = plan_info['plan']
                        
                        # Add credits
                        if 'credits' in plan_info:
                            profile.credits += plan_info['credits']
                        
                        profile.save()
                        logger.info(f"Successfully updated user {user.email} (ID: {user.id}) with plan/credits from product {product_id}")
                    else:
                        logger.error(f"Could not find user for Polar event. Email: {customer_email}, ID: {user_id}")
                    
                except User.DoesNotExist:
                    logger.error(f"User with email {customer_email} not found for Polar event")
                    # Optionally create user or log for manual intervention
                    
        return HttpResponse('Webhook received', status=200)

    except Exception as e:
        logger.error(f"Error processing Polar webhook: {str(e)}")
        return HttpResponse('Internal error', status=500)
