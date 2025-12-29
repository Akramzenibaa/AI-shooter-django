from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
import logging
from polar_sdk import Polar

def profile(request):
    return render(request, 'accounts/profile.html')

@login_required
def create_checkout(request, product_id):
    """
    Creates a Polar checkout session and redirects the user.
    """
    if not settings.POLAR_ACCESS_TOKEN:
        # Fallback or error if token not configured
        messages.error(request, "Payments are not currently configured.")
        return redirect('core:pricing')
    
    try:
        # DBG: Log token prefix to verify update
        token_prefix = settings.POLAR_ACCESS_TOKEN[:15] if settings.POLAR_ACCESS_TOKEN else "None"
        server = getattr(settings, 'POLAR_ENVIRONMENT', 'production')
        logger = logging.getLogger(__name__)
        logger.info(f"DEBUG: Using Polar Token: {token_prefix}..., Env: {server}")

        # Use sandbox server if POLAR_ENVIRONMENT is set to 'sandbox'
        with Polar(access_token=settings.POLAR_ACCESS_TOKEN, server=server) as polar:
            # We use the product_id passed from the template
            checkout_request = {
                "products": [product_id],
                "success_url": request.build_absolute_uri(reverse('core:dashboard')) + "?payment=success",
                "metadata": {"user_id": str(request.user.id)},
            }
            
            # Only include email if it's likely valid and not a default/test one
            if request.user.email and '@example.com' not in request.user.email:
                checkout_request["customer_email"] = request.user.email
                
            checkout = polar.checkouts.create(request=checkout_request)
            return redirect(checkout.url)
    except Exception as e:
        # Log error and return to pricing
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating Polar checkout for product {product_id}: {str(e)}")
        logger.error(traceback.format_exc())
        messages.error(request, "An error occurred while setting up the checkout. Please try again.")
        return redirect('core:pricing')
