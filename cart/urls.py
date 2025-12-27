from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_view, name='cart'),
    path('add/<int:id>/', views.add_to_cart_view, name='add_to_cart'),
    path('remove/<int:id>/', views.remove_from_cart_view, name='remove_from_cart'),
]