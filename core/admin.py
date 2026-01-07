from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'get_subject_display', 'created_at', 'is_read']
    list_filter = ['subject', 'is_read', 'created_at']
    search_fields = ['full_name', 'email', 'message']
    list_editable = ['is_read']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def get_subject_display(self, obj):
        return obj.get_subject_display()
    get_subject_display.short_description = 'موضوع'