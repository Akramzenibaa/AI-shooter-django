from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile
from apps.images.models import GeneratedImage
from django.utils.safestring import mark_safe

# --- INLINES ---

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Credits & Profile'

class GeneratedImageInline(admin.TabularInline):
    model = GeneratedImage
    extra = 0
    readonly_fields = ('image_preview', 'created_at', 'count', 'image_url')
    fields = ('image_preview', 'created_at', 'count', 'image_url')

    def image_preview(self, obj):
        if obj.image_url:
            return mark_safe(f'<img src="{obj.image_url}" style="max-height: 50px; border-radius: 2px;" />')
        return "No image"
    image_preview.short_description = "Pic"

# --- MASTER USER ADMIN ---

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, GeneratedImageInline)
    list_display = BaseUserAdmin.list_display + ('get_credits',)

    def get_credits(self, obj):
        return obj.userprofile.credits
    get_credits.short_description = 'Credits'

# Re-register User with new capabilities
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Hide the separate UserProfile model to keep the sidebar clean
# admin.site.register(UserProfile) # Already registered in old code, now implicitly part of User
