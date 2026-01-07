from django.contrib import admin
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'publish_date', 'views']
    list_filter = ['status', 'category', 'author']
    search_fields = ['title', 'content']
    date_hierarchy = 'publish_date'
    readonly_fields = ['views', 'created_at', 'updated_at']
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'content', 'image', 'category')
        }),
        ('تنظیمات انتشار', {
            'fields': ('author', 'publish_date', 'status')
        }),
        ('اطلاعات سیستمی', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )