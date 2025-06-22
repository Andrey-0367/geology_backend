from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Prefetch
from .models import (
    ContactMessage, Employee, Category, Product,
    Order, OrderItem, SaleItem, SaleItemImage, ProductImage
)
from .serializers import (
    ContactMessageSerializer,
    EmployeeSerializer,
    CategorySerializer,
    ProductSerializer,
    ProductImageSerializer,
    OrderSerializer,
    SaleItemSerializer,
    SaleItemImageSerializer
)


class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    http_method_names = ['post']


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_serializer_context(self):
        return {'request': self.request}


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_serializer_context(self):
        return {'request': self.request}


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.prefetch_related(
            Prefetch('images',
                queryset=ProductImage.objects.order_by('order'),
                to_attr='prefetched_images'
            )
        ).select_related('category')

    def get_serializer_context(self):
        return {'request': self.request}


class ProductImageViewSet(viewsets.ModelViewSet):
    serializer_class = ProductImageSerializer
    parser_classes = (MultiPartParser, FormParser)
    queryset = ProductImage.objects.all()

    def get_queryset(self):
        product_id = self.request.query_params.get('product')
        if product_id:
            return ProductImage.objects.filter(product_id=product_id)
        return super().get_queryset()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('items')
    serializer_class = OrderSerializer
    http_method_names = ['post']


class SaleItemViewSet(viewsets.ModelViewSet):
    serializer_class = SaleItemSerializer

    def get_queryset(self):
        return SaleItem.objects.prefetch_related(
            Prefetch('images',
                queryset=SaleItemImage.objects.order_by('order'),
                to_attr='prefetched_images'
            )
        ).filter(is_active=True)

    def get_serializer_context(self):
        return {'request': self.request}


class SaleItemImageViewSet(viewsets.ModelViewSet):
    serializer_class = SaleItemImageSerializer
    parser_classes = (MultiPartParser, FormParser)
    queryset = SaleItemImage.objects.all()

    def get_queryset(self):
        sale_item_id = self.request.query_params.get('sale_item')
        if sale_item_id:
            return SaleItemImage.objects.filter(sale_item_id=sale_item_id)
        return super().get_queryset()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
