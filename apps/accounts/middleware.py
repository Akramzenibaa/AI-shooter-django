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
                reverse('core:landing'),
                '/admin/',
                '/static/',
                '/media/',
            ]
            
            # Check if user has a profile and is missing a phone number
            if hasattr(request.user, 'userprofile') and not request.user.userprofile.phone_number:
                current_path = request.path
                
                # If they are not on an allowed path, redirect them to the profile page
                # Special cases for logout and landing which might be prefixes of other things
                if current_path == reverse('core:landing') or current_path == reverse('account_logout'):
                    is_allowed = True
                else:
                    is_allowed = any(current_path.startswith(path) for path in allowed_paths)
                
                if not is_allowed:
                    return redirect('accounts:profile')
                    
        response = self.get_response(request)
        return response
