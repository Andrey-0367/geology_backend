from django.urls import path, include
from rest_framework import routers
from .views import ContactMessageViewSet, EmployeeViewSet, CategoryViewSet, ProductViewSet, OrderViewSet, \
    SaleItemViewSet, SaleItemImageViewSet


api_urls: list = []
v1_router_api = routers.DefaultRouter()

v1_router_api.register(r'contact', ContactMessageViewSet, basename='contact-messages')
v1_router_api.register(r'employees', EmployeeViewSet, basename='employees')
v1_router_api.register(r'categories', CategoryViewSet)
v1_router_api.register(r'products', ProductViewSet)
v1_router_api.register(r'orders', OrderViewSet, basename='order')
v1_router_api.register(r'sale-items', SaleItemViewSet, basename='sale-items')
v1_router_api.register(r'sale-item-images', SaleItemImageViewSet, basename='sale-item-images')

api_urls.extend(v1_router_api.urls)

urlpatterns = [
    path('v1/', include(api_urls)),
]
