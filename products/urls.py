from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list_view, name='product_list'),
    path('<int:id>/', views.product_detail_view, name='product_detail'),
    path('category/<slug:slug>/', views.category_view, name='category_detail'),
]