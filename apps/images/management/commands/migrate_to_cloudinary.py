import os
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.images.models import GeneratedImage
import cloudinary
import cloudinary.uploader

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Migrates locally stored generated images to Cloudinary'

    def handle(self, *args, **options):
        # 1. Configure Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
            secure=True
        )

        images = GeneratedImage.objects.filter(image_url__contains='/media/')
        
        if not images.exists():
            self.stdout.write(self.style.SUCCESS('No local images found for migration.'))
            return

        self.stdout.write(f"Found {images.count()} local images. Starting migration...")

        count = 0
        for img in images:
            try:
                # Resolve local path
                # Local URL is like /media/generated_campaigns/filename.png
                relative_path = img.image_url.replace(settings.MEDIA_URL, '')
                local_path = os.path.join(settings.MEDIA_ROOT, relative_path)

                if os.path.exists(local_path):
                    self.stdout.write(f"Uploading {local_path}...")
                    
                    filename = os.path.basename(local_path)
                    upload_res = cloudinary.uploader.upload(
                        local_path,
                        folder="generated_campaigns",
                        public_id=filename.split('.')[0], # Remove extension from public_id
                        overwrite=True
                    )
                    
                    new_url = upload_res.get('secure_url')
                    if new_url:
                        img.image_url = new_url
                        img.save()
                        count += 1
                        self.stdout.write(self.style.SUCCESS(f"Successfully migrated: {new_url}"))
                else:
                    self.stdout.write(self.style.WARNING(f"File not found on disk: {local_path}"))
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to migrate image {img.id}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f"Migration complete! {count} images promoted to Cloudinary."))
