from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom account adapter to suppress verification emails during social flows"""
    
    def is_email_verification_required(self, request, email):
        if "/google/" in request.path or "/social/" in request.path:
            return False
        return super().is_email_verification_required(request, email)

    def send_mail(self, template_prefix, email, context):
        if "/google/" in self.request.path or "/social/" in self.request.path:
            return
        super().send_mail(template_prefix, email, context)

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        if "/google/" in request.path or "/social/" in request.path:
            return
        super().send_confirmation_mail(request, emailconfirmation, signup)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom social account adapter to skip email verification when connecting accounts"""
    
    def is_auto_signup_allowed(self, request, sociallogin):
        return True
    
    def pre_social_login(self, request, sociallogin):
        """
        Force verification state in DB and session for social logins.
        """
        from allauth.account.models import EmailAddress
        
        # 1. Mark the social email object as verified
        for email_obj in sociallogin.email_addresses:
            email_obj.verified = True
            
            # 2. Sync with the database record for this email
            # This handles cases where a manual account was created but not verified
            EmailAddress.objects.filter(email=email_obj.email).update(verified=True)

        # 3. If there's an existing user, ensure their EmailAddress objects are verified
        if sociallogin.is_existing:
            EmailAddress.objects.filter(user=sociallogin.user, email=sociallogin.user.email).update(verified=True)

