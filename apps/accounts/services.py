import os
import requests
from django.conf import settings

class EmailService:
    def __init__(self):
        self.api_key = os.getenv('RESEND_API_KEY')
        self.url = "https://api.resend.com/emails"

    def send_welcome_email(self, to_email, user_name):
        if not self.api_key:
            print(f"[TEST EMAIL] To: {to_email}, Subject: Welcome, Body: Hello {user_name}!")
            return
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        data = {
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": [to_email],
            "subject": "Welcome to AI Shooter!",
            "html": f"<strong>Hello {user_name}!</strong><p>Thanks for joining AI Shooter. You have 10 free credits to start shooting!</p>",
        }
        
        response = requests.post(self.url, headers=headers, json=data)
        return response.json()
