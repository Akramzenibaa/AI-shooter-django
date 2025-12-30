from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free Trial'),
        ('starter', 'Starter Shop'),
        ('growth', 'Growth Brand'),
        ('agency', 'Agency Elite'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credits = models.IntegerField(default=3) # Default free trial
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return self.user.email

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
