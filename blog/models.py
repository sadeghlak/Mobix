from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# لیست ثابت دسته‌بندی‌ها
CATEGORY_CHOICES = [
    ('tech', 'تکنولوژی و کالای دیجیتال'),
    ('game', 'بازی و سرگرمی'),
    ('edu', 'آموزش'),
]

# وضعیت‌های مقاله
STATUS_CHOICES = [
    ('draft', 'پیش‌نویس'),
    ('published', 'منتشر شده'),
]

class Article(models.Model):
    # ۱. عنوان مقاله
    title = models.CharField(max_length=200, verbose_name="عنوان مقاله")
    
    # ۲. محتوای مقاله
    content = models.TextField(verbose_name="محتوا")
    
    # ۳. عکس مقاله
    image = models.ImageField(
        upload_to='articles/images/',
        verbose_name="عکس مقاله",
        null=True,
        blank=True
    )
    
    # ۴. دسته‌بندی (از لیست ثابت)
    category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
        verbose_name="دسته‌بندی"
    )
    
    # ۵. نویسنده
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name="نویسنده",
        null=True,  # اضافه کن
        blank=False  # اضافه کن
    )
    
    # ۶. تاریخ انتشار
    publish_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="تاریخ انتشار"
    )
    
    # ۷. وضعیت مقاله
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="وضعیت"
    )
    
    # ۸. تاریخ‌های سیستمی
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")
    
    # ۹. بازدیدها
    views = models.PositiveIntegerField(default=0, verbose_name="تعداد بازدید")
    
    class Meta:
        verbose_name = "مقاله"
        verbose_name_plural = "مقالات"
        ordering = ['-publish_date', '-created_at']
    
    def __str__(self):
        return self.title
    
    def get_category_display_fa(self):
        """نمایش فارسی دسته‌بندی"""
        for code, name in CATEGORY_CHOICES:
            if code == self.category:
                return name
        return self.category