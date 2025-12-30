from django.shortcuts import redirect
from django.urls import reverse

class PhoneMandatoryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Paths that are allowed even without a phone number
            # Specific paths that are allowed without a phone number
            exact_allowed = [
                reverse('accounts:profile'),
                reverse('account_logout'),
                reverse('core:landing'),
            ]
            
            # Prefix paths that are allowed (admin, static files)
            prefix_allowed = [
                '/admin/',
                '/static/',
                '/media/',
            ]
            
            # Check if user has a profile and is missing a phone number
            if hasattr(request.user, 'userprofile') and not request.user.userprofile.phone_number:
                current_path = request.path
                
                # Check exact matches first
                is_allowed = current_path in exact_allowed
                
                # Check prefix matches if not already allowed
                if not is_allowed:
                    is_allowed = any(current_path.startswith(prefix) for prefix in prefix_allowed)
                
                if not is_allowed:
                    return redirect('accounts:profile')
                    
        response = self.get_response(request)
        return response
