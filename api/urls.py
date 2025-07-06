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
    RobotsTxtView
)

simple_urls = [
    path('orders/', OrderViewSet.as_view({'post': 'create'}), name='order-create'),
    path('robots.txt', RobotsTxtView.as_view(), name='robots_txt'),
]


v1_urls = [
    path('categories/<int:category_id>/filters/', CategoryFiltersView.as_view(), name='category-filters'),
    path('products/filters/', ProductViewSet.as_view({'get': 'filters'}), name='product-filters'),
]

v1_router = routers.DefaultRouter()
v1_router.register(r'contact', ContactMessageViewSet, basename='contact-messages')
v1_router.register(r'employees', EmployeeViewSet, basename='employees')
v1_router.register(r'categories', CategoryViewSet, basename='categories')
v1_router.register(r'products', ProductViewSet, basename='products')
v1_router.register(r'product-images', ProductImageViewSet, basename='product-images')
v1_router.register(r'sale-items', SaleItemViewSet, basename='sale-items')
v1_router.register(r'sale-item-images', SaleItemImageViewSet, basename='sale-item-images')

v1_urls += v1_router.urls

urlpatterns = [
    *simple_urls,
    path('v1/', include(v1_urls)),
]