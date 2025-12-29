from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
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
        return redirect('core:pricing')
    
    try:
        # Use sandbox URL if needed for testing, otherwise default is production
        with Polar(access_token=settings.POLAR_ACCESS_TOKEN) as polar:
            # We use the product_id passed from the template
            checkout = polar.checkouts.create(request={
                "products": [product_id],
                "success_url": request.build_absolute_uri('/dashboard/') + "?payment=success",
                "customer_email": request.user.email,
                # Optionally add metadata for robust correlation
                # "metadata": {"user_id": str(request.user.id)}
            })
            return redirect(checkout.url)
    except Exception as e:
        # Log error and return to pricing
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating Polar checkout: {str(e)}")
        return redirect('core:pricing')
