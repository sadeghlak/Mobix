from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
     # ==================== مدیریت پیام‌های تماس ====================
    path('contact-messages/', views.contact_messages_list, name='contact_messages_list'),
    path('contact-message/<int:message_id>/toggle-read/', views.toggle_message_read, name='toggle_read'),
    path('contact-message/<int:message_id>/content/', views.get_message_content, name='get_message_content'),
    path('contact-message/<int:message_id>/delete/', views.delete_message, name='delete_message'),
    path('contact-message/<int:message_id>/reply/', views.reply_to_message, name='reply_to_message'),
    path('contact-messages/mark-all-read/', views.mark_all_as_read, name='mark_all_read'),
    path('contact-messages/delete-read/', views.delete_read_messages, name='delete_read'),
    
    # ==================== مدیریت کاربران ====================
    path('users/', views.users_list, name='users_list'),
    path('users/add/', views.add_user, name='add_user'),
    path('user/<int:user_id>/', views.user_detail, name='user_detail'),
    path('user/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('user/<int:user_id>/toggle-active/', views.toggle_user_active, name='toggle_user_active'),
    path('user/<int:user_id>/toggle-staff/', views.toggle_user_staff, name='toggle_user_staff'),
    path('user/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('users/bulk-action/', views.bulk_users_action, name='bulk_users_action'),
    path('users/search/', views.search_users_ajax, name='search_users_ajax'),
    
    # ==================== مدیریت مقالات ====================
    path('blog/', views.blog_list_view, name='blog_list'),
    path('blog/add/', views.blog_create_view, name='blog_create'),
    path('blog/<int:article_id>/', views.blog_detail_view, name='blog_detail'),
    path('blog/<int:article_id>/edit/', views.blog_edit_view, name='blog_edit'),
    path('blog/<int:article_id>/delete/', views.blog_delete_view, name='blog_delete'),
    path('blog/<int:article_id>/toggle-status/', views.toggle_article_status, name='toggle_article_status'),
    path('blog/bulk-action/', views.bulk_articles_action, name='bulk_articles_action'),
    
]