from django.shortcuts import redirect
from django.urls import reverse

class PhoneMandatoryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Paths that are allowed even without a phone number
            allowed_paths = [
                reverse('accounts:profile'),
                reverse('account_logout'),
                '/admin/',  # Allow admin access
                '/static/',  # Allow static files
                '/media/',   # Allow media files
            ]
            
            # Check if user has a profile and is missing a phone number
            if hasattr(request.user, 'userprofile') and not request.user.userprofile.phone_number:
                # If they are not on an allowed path, redirect them to the profile page
                current_path = request.path
                is_allowed = any(current_path.startswith(path) for path in allowed_paths)
                
                if not is_allowed:
                    return redirect('accounts:profile')
                    
        response = self.get_response(request)
        return response
