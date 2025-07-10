from django.core.mail import send_mail
from django.db.models import Count
from django.views.decorators.csrf import csrf_protect
from rest_framework import viewsets, mixins, status
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
import logging
import threading

from .permissions import IsSuperUserOrReadOnly
from .models import ContactMessage, Employee, Category, Product, Order, SaleItemImage, SaleItem, ProductImage
from .serializers import ContactMessageSerializer, EmployeeSerializer, CategorySerializer, ProductSerializer, \
    OrderSerializer, SaleItemImageSerializer, SaleItemSerializer, ProductImageSerializer, CategoryProductsSerializer

logger = logging.getLogger(__name__)


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
    permission_classes = [IsSuperUserOrReadOnly]

    def get_serializer_context(self):
        return {'request': self.request}

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        category = self.get_object()
        products = Product.objects.filter(category=category).prefetch_related('images')
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CategoryProductsSerializer(instance, context={'request': request})
        return Response(serializer.data)


def get_filter_counts(queryset, filter_fields):
    """Возвращает доступные значения фильтров и их количество"""
    result = {}
    for field in filter_fields:
        # Группируем и считаем количество
        aggregation = (
            queryset
            .exclude(**{field: None})
            .exclude(**{field: ""})
            .values(field)
            .annotate(count=Count('id'))
            .order_by(field)
        )

        result[field] = [
            {"value": item[field], "count": item["count"]}
            for item in aggregation
        ]
    return result


class CategoryFiltersView(APIView):
    filter_fields = [
        'size', 'brand', 'thread_connection',
        'thread_connection_2', 'armament', 'seal', 'iadc'
    ]

    def get(self, request, category_id):
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=404)

        # Применяем фильтры из запроса
        filters = {}
        for field in self.filter_fields:
            value = request.query_params.get(field)
            if value:
                filters[f"{field}__exact"] = value

        # Фильтр по наличию
        availability = request.query_params.get('availability')
        if availability == 'in-stock':
            filters['quantity__gt'] = 0
        elif availability == 'out-of-stock':
            filters['quantity'] = 0

        # Получаем продукты с учетом фильтров
        products = Product.objects.filter(category=category, **filters)

        # Используем общую функцию для получения фильтров
        result = get_filter_counts(products, self.filter_fields)
        return Response(result)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().prefetch_related('images')
    serializer_class = ProductSerializer
    permission_classes = [IsSuperUserOrReadOnly]
    filter_fields = [
        'size', 'brand', 'thread_connection',
        'thread_connection_2', 'armament', 'seal', 'iadc'
    ]

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        queryset = super().get_queryset()

        # Фильтрация по категории
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # Фильтрация по наличию
        availability = self.request.query_params.get('availability')
        if availability == 'in-stock':
            queryset = queryset.filter(quantity__gt=0)
        elif availability == 'out-of-stock':
            queryset = queryset.filter(quantity=0)

        # Применяем дополнительные фильтры
        for field in self.filter_fields:
            value = self.request.query_params.get(field)
            if value:
                queryset = queryset.filter(**{field: value})

        return queryset

    @action(detail=False, methods=['get'])
    def filters(self, request):
        """Возвращает доступные фильтры для продуктов"""
        # Получаем базовый queryset
        queryset = self.filter_queryset(self.get_queryset())

        # Используем общую функцию для получения фильтров
        result = get_filter_counts(queryset, self.filter_fields)
        return Response(result)


class ProductImageViewSet(viewsets.ModelViewSet):
    serializer_class = ProductImageSerializer
    parser_classes = (MultiPartParser, FormParser)
    queryset = ProductImage.objects.all()
    permission_classes = [IsSuperUserOrReadOnly]

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
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    http_method_names = ['get', 'post']
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        # Сохраняем заказ
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        # Запускаем отправку email в фоновом режиме
        try:
            threading.Thread(
                target=self.send_simple_email,
                args=(order,),
                daemon=True
            ).start()
        except Exception as e:
            logger.error(f"Failed to start email thread: {str(e)}")

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def send_simple_email(self, order):
        """Минимальная отправка уведомления администратору"""
        try:
            subject = f'🛒 Новый заказ #{order.id}'
            message = (
                f"Поступил новый заказ!\n\n"
                f"🔹 Номер: {order.id}\n"
                f"👤 Клиент: {order.first_name} {order.last_name}\n"
                f"📞 Телефон: {order.phone}\n"
                f"✉️ Email: {order.email}\n"
                f"📍 Адрес: {order.city}, {order.address}\n"
                f"💰 Сумма: {order.total} руб.\n\n"
                f"📦 Товары:\n"
            )

            # Добавляем информацию о товарах
            for i, product in enumerate(order.products, 1):
                message += (
                    f"{i}. {product.get('name', 'Без названия')} - "
                    f"{product.get('quantity', 1)} шт. x "
                    f"{product.get('price', 0)} руб.\n"
                )

            # Отправляем письмо только администратору
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_HOST_USER],
                fail_silently=False
            )
            logger.info(f"Order email sent for order #{order.id}")

        except Exception as e:
            logger.error(f"Email sending failed for order #{order.id}: {str(e)}")


class SaleItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperUserOrReadOnly]
    queryset = SaleItem.objects.prefetch_related('images').all()
    serializer_class = SaleItemSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset.filter(is_active=True)
        return self.queryset


class SaleItemImageViewSet(viewsets.ModelViewSet):
    serializer_class = SaleItemImageSerializer
    queryset = SaleItemImage.objects.all()
    permission_classes = [IsSuperUserOrReadOnly]

    def get_queryset(self):
        sale_item_id = self.request.query_params.get('sale_item')
        if sale_item_id:
            return SaleItemImage.objects.filter(sale_item_id=sale_item_id)
        return super().get_queryset()
