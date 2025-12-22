from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import GeneratedImage

@admin.register(GeneratedImage)
class GeneratedImageAdmin(admin.ModelAdmin):
    list_display = ('user', 'image_preview', 'created_at', 'count', 'image_url')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'user__email', 'image_url')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image_url:
            return mark_safe(f'<img src="{obj.image_url}" style="max-height: 100px; border-radius: 4px;" />')
        return "No image"
    image_preview.short_description = "Preview"
