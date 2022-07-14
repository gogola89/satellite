from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth import get_user_model
from django.utils.html import format_html
import admin_thumbnails

# Register your models here.
User = get_user_model()


@admin.register(User)
class AccountAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    def thumbnail(self, object):
        return format_html('<img src="{}" width="30" style="border-radius:50%;" alt="User Photo">'.format(object.profileURL))

    thumbnail.short_description = "Profile Picture"

    list_display = ['thumbnail', 'full_name', 'email',
                    'phone_number', 'country', 'date_joined', 'is_active']

    fieldsets = (
        (None, {'fields': ('full_name', 'profile_picture',
         'email', 'phone_number', 'country', 'password')}),
        ('Permissions', {'fields': ('is_admin',
         'is_superuser', 'is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('full_name', 'profile_picture', 'email', 'phone_number', 'country', 'password1', 'password2', 'is_admin', 'is_superuser', 'is_staff', 'is_active')}
         ),
    )

    list_filter = ['date_joined', 'is_active']
    list_display_links = ['full_name', 'email']
    ordering = ['-date_joined']
