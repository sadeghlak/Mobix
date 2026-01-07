from django.db import models

class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('suggestion', 'پیشنهاد'),
        ('criticism', 'انتقاد'),
        ('support', 'پشتیبانی'),
        ('cooperation', 'همکاری'),
        ('other', 'سایر'),
    ]
    
    full_name = models.CharField(max_length=100, verbose_name="نام کامل")
    email = models.EmailField(verbose_name="ایمیل")
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, verbose_name="موضوع")
    message = models.TextField(verbose_name="پیام")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال")
    is_read = models.BooleanField(default=False, verbose_name="خوانده شده")
    
    class Meta:
        verbose_name = "پیام تماس"
        verbose_name_plural = "پیام‌های تماس"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.get_subject_display()}"