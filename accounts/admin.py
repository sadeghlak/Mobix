from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'address', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    list_filter = ['created_at']

# یا اگر می‌خواهید User رو هم سفارشی‌سازی کنید:
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'date_joined']
    list_filter = ['is_staff', 'is_active']

admin.site.unregister(User)  # ثبت قبلی رو حذف کن
admin.site.register(User, CustomUserAdmin)  # با نسخه سفارشی ثبت کن