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

v1_router_api = routers.DefaultRouter()
v1_router_api.register(r'contact', ContactMessageViewSet, basename='contact-messages')
v1_router_api.register(r'employees', EmployeeViewSet, basename='employees')
v1_router_api.register(r'categories', CategoryViewSet, basename='categories')
v1_router_api.register(r'products', ProductViewSet, basename='products')
v1_router_api.register(r'product-images', ProductImageViewSet, basename='product-images')
v1_router_api.register(r'sale-items', SaleItemViewSet, basename='sale-items')
v1_router_api.register(r'sale-item-images', SaleItemImageViewSet, basename='sale-item-images')
v1_router_api.register(r'orders', OrderViewSet, basename='orders')

api_urls = [
    path('categories/<int:category_id>/filters/', CategoryFiltersView.as_view(), name='category-filters'),
    path('products/filters/', ProductViewSet.as_view({'get': 'filters'}), name='product-filters'),
]


api_urls.extend(v1_router_api.urls)

urlpatterns = [
    path('v1/', include(api_urls)),
]
