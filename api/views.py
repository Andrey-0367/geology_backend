from django.conf import settings
from django.core.mail import send_mail
from rest_framework import permissions, viewsets, mixins
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Prefetch
from .models import ContactMessage, Employee, Category, Product, Order, SaleItemImage, SaleItem, ProductImage
from .permissions import IsSuperUserOrReadOnly
from .serializers import ContactMessageSerializer, EmployeeSerializer, ProductImageSerializer, SaleItemSerializer, \
    OrderSerializer, SaleItemImageSerializer, CategorySerializer, ProductSerializer


class ContactMessageViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    http_method_names = ['post']

    def perform_create(self, serializer):
        instance = serializer.save()
        send_mail(
            subject='Новое сообщение с сайта Geology',
            message=f'От: {instance.email}\n\nСообщение: {instance.message}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )


class EmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsSuperUserOrReadOnly]
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
        ).select_related('category').order_by('id')

    def get_serializer_context(self):
        return {'request': self.request}


class ProductImageViewSet(viewsets.ModelViewSet):
    serializer_class = ProductImageSerializer
    parser_classes = (MultiPartParser, FormParser)
    queryset = ProductImage.objects.all()
    permission_classes = [IsSuperUserOrReadOnly]

    def get_queryset(self):
        product_id = self.request.query_params.get('product')
        if product_id:
            return ProductImage.objects.filter(product_id=product_id).order_by('order')
        return super().get_queryset().order_by('order')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('items').order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    http_method_names = ['post']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Order.objects.filter(user=user)
        return Order.objects.none()

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()


class SaleItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperUserOrReadOnly]
    serializer_class = SaleItemSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = SaleItem.objects.prefetch_related(
            Prefetch('images',
                queryset=SaleItemImage.objects.order_by('order'),
                to_attr='prefetched_images'
            )
        ).order_by('-created_at')

        if self.action == 'list':
            return queryset.filter(is_active=True)
        return queryset

    def get_serializer_context(self):
        return {'request': self.request}


class SaleItemImageViewSet(viewsets.ModelViewSet):
    serializer_class = SaleItemImageSerializer
    queryset = SaleItemImage.objects.all()
    permission_classes = [IsSuperUserOrReadOnly]

    def get_queryset(self):
        sale_item_id = self.request.query_params.get('sale_item')
        if sale_item_id:
            return SaleItemImage.objects.filter(sale_item_id=sale_item_id).order_by('order')
        return super().get_queryset().order_by('order')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
