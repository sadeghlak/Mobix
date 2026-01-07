from django.urls import path
# from . import views

# urlpatterns = [
#     path('login/', views.login_view, name='login'),
#     path('register/', views.register_view, name='register'),
#     path('logout/', views.logout_view, name='logout'),
# ]

from django.contrib.auth import views as auth_views
from accounts import views as accounts_views

urlpatterns = [
    # ... دیگر URLها
    path('login/', accounts_views.login_view, name='login'),
    path('register/', accounts_views.register_view, name='register'),
    path('logout/', accounts_views.logout_view, name='logout'),
    path('profile/', accounts_views.profile_view, name='profile'),
]