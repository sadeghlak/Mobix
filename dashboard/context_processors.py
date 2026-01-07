from core.models import ContactMessage

def dashboard_context(request):
    """
    Context Processor برای نمایش تعداد پیام‌های نخوانده در منوی داشبورد
    """
    if request.user.is_authenticated and request.user.is_staff:
        unread_count = ContactMessage.objects.filter(is_read=False).count()
        return {
            'unread_messages_count': unread_count,
        }
    return {}