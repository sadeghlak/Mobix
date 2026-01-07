from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

class Profile(models.Model):
    """
    مدل پروفایل کاربر برای ذخیره اطلاعات تکمیلی
    کلید ارتباطی: user (به مدل User پیش‌فرض جنگو)
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('کاربر')
    )
    
    phone = models.CharField(
        _('تلفن همراه'),
        max_length=15,
        blank=True,
        null=True,  # بهتره null=True هم داشته باشه
        unique=True,  # شماره تلفن باید یکتا باشه
        db_index=True,  # برای جستجوی سریع‌تر
        help_text=_('مثال: 09123456789')
    )
    
    address = models.TextField(
        _('آدرس'),
        blank=True,
        null=True,
        help_text=_('آدرس کامل پستی')
    )
    
    created_at = models.DateTimeField(
        _('تاریخ ایجاد'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _('آخرین به‌روزرسانی'),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _('پروفایل')
        verbose_name_plural = _('پروفایل‌ها')
        ordering = ['-created_at']  # مرتب‌سازی بر اساس تاریخ ایجاد
        indexes = [
            models.Index(fields=['phone']),  # ایندکس برای جستجوی سریع‌تر
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f'پروفایل {self.user.username}'
    
    @property
    def email(self):
        """دسترسی به ایمیل کاربر از طریق پروفایل"""
        return self.user.email
    
    @property
    def has_completed_profile(self):
        """آیا پروفایل کامل شده؟ (شماره تلفن و آدرس وارد شده)"""
        return bool(self.phone and self.address)
    
    @property
    def profile_completion_percentage(self):
        """درصد تکمیل پروفایل"""
        required_fields = [self.phone, self.address]
        completed = sum(1 for field in required_fields if field)
        return int((completed / len(required_fields)) * 100) if required_fields else 0

# سیگنال برای ساخت خودکار پروفایل
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    هر کاربر جدید که ایجاد شود، پروفایلش هم ساخته شود
    """
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    هر بار کاربر ذخیره شد، پروفایلش هم ذخیره شود
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        # اگر پروفایل وجود نداشت، ایجادش کن
        Profile.objects.get_or_create(user=instance)
        

# ایجاد مدل manager

# class ManagerProfile(models.Model):
#     """
#     پروفایل مدیران سایت (تفکیک از کاربران عادی)
#     """
#     user = models.OneToOneField(
#         User,
#         on_delete=models.CASCADE,
#         related_name='manager_profile'
#     )
    
#     ROLE_CHOICES = [
#         ('super_admin', 'سوپر ادمین'),
#         ('product_manager', 'مدیر محصولات'),
#         ('order_manager', 'مدیر سفارشات'),
#         ('content_manager', 'مدیر محتوا'),
#     ]
    
#     role = models.CharField(
#         'نقش',
#         max_length=50,
#         choices=ROLE_CHOICES,
#         default='product_manager'
#     )
    
#     permissions = models.JSONField(
#         'دسترسی‌ها',
#         default=list,
#         help_text='لیست دسترسی‌های خاص'
#     )
    
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         verbose_name = 'پروفایل مدیر'
#         verbose_name_plural = 'پروفایل‌های مدیران'
    
#     def __str__(self):
#         return f'{self.user.username} - {self.get_role_display()}'