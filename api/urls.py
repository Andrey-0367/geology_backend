from django.urls import path, include
from rest_framework import routers
from .views import (
    ContactMessageViewSet,
    EmployeeViewSet,
    CategoryViewSet,
    ProductViewSet,
    OrderViewSet,
    SaleItemViewSet,
    SaleItemImageViewSet,
    ProductImageViewSet,
    CategoryFiltersView,
)

# Создаем основной роутер для API v1
v1_router = routers.DefaultRouter()
v1_router.register(r'contact', ContactMessageViewSet, basename='contact-messages')
v1_router.register(r'employees', EmployeeViewSet, basename='employees')
v1_router.register(r'categories', CategoryViewSet, basename='categories')
v1_router.register(r'products', ProductViewSet, basename='products')
v1_router.register(r'product-images', ProductImageViewSet, basename='product-images')
v1_router.register(r'sale-items', SaleItemViewSet, basename='sale-items')
v1_router.register(r'sale-item-images', SaleItemImageViewSet, basename='sale-item-images')
v1_router.register(r'orders', OrderViewSet, basename='orders')

# Кастомные пути для API v1
v1_custom_urls = [
    path('categories/<int:category_id>/filters/', CategoryFiltersView.as_view(), name='category-filters'),
    path('products/filters/', ProductViewSet.as_view({'get': 'filters'}), name='product-filters'),
]

# Объединяем все пути API v1
v1_urlpatterns = [
    path('', include(v1_router.urls)),
    *v1_custom_urls,
]

# Основные URL patterns
urlpatterns = [
    path('v1/', include(v1_urlpatterns)),
]