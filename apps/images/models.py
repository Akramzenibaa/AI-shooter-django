from django.db import models
from django.contrib.auth.models import User

class GeneratedImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_images')
    original_image = models.ImageField(upload_to='originals/')
    image_url = models.URLField(max_length=500) # Drive link or local path
    created_at = models.DateTimeField(auto_now_add=True)
    count = models.IntegerField(default=1)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.created_at}"
