from django.core.mail import send_mail
from django.db.models import Count
from django.views import View
from rest_framework import viewsets, mixins
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.middleware.csrf import get_token
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .permissions import IsSuperUserOrReadOnly
from .models import ContactMessage, Employee, Category, Product, Order, SaleItemImage, SaleItem, ProductImage
from .serializers import ContactMessageSerializer, EmployeeSerializer, CategorySerializer, ProductSerializer, \
    OrderSerializer, SaleItemImageSerializer, SaleItemSerializer, ProductImageSerializer, CategoryProductsSerializer


class RobotsTxtView(View):
    def get(self, request):
        lines = [
            "User-agent: *",
            "Disallow: /admin/",
            "Disallow: /api/",
            "Allow: /",
            f"Sitemap: {settings.SITE_URL}/sitemap.xml"
        ]
        return HttpResponse("\n".join(lines), content_type="text/plain")


@api_view(['GET'])
@permission_classes([AllowAny])
def get_csrf_token(request):
    """Вьюха для получения CSRF-токена"""
    token = get_token(request)
    response = JsonResponse({'csrfToken': token})
    response.set_cookie(
        'csrftoken',
        token,
        domain=settings.CSRF_COOKIE_DOMAIN,
        secure=settings.CSRF_COOKIE_SECURE,
        samesite=settings.CSRF_COOKIE_SAMESITE,
        httponly=settings.CSRF_COOKIE_HTTPONLY
    )
    return response


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
    serializer_class = OrderSerializer
    http_method_names = ['post']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Order.objects.filter(user=user)
        return Order.objects.none()

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            order = serializer.save(user=self.request.user)
        else:
            order = serializer.save()

        # Отправляем письмо подтверждения
        order.send_confirmation_email()


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
