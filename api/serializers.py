from rest_framework import serializers
from .models import ContactMessage, Employee, Category, Product, OrderItem, Order, SaleItem, SaleItemImage, ProductImage
import logging

logger = logging.getLogger(__name__)


class BaseImageSerializer:
    def get_image_url(self, obj, image_field):
        request = self.context.get('request')
        if not request:
            return None

        if not image_field:
            return None

        try:
            if hasattr(image_field, 'url') and image_field.url:
                return request.build_absolute_uri(image_field.url)
        except ValueError as e:
            logger.error(f"File not found: {str(e)}")
        except Exception as e:
            logger.exception("Error processing image")

        return None


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = '__all__'

    def get_photo_url(self, obj):
        return self.get_image_url(obj, obj.photo) if hasattr(self, 'get_image_url') else None


class CategorySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'image_url']

    def get_image_url(self, obj):
        return self.get_image_url(obj, obj.image) if hasattr(self, 'get_image_url') else None


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'is_main', 'order', 'product']

    def get_image_url(self, obj):
        return self.get_image_url(obj, obj.image) if hasattr(self, 'get_image_url') else None


class ProductSerializer(serializers.ModelSerializer, BaseImageSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    main_image = serializers.SerializerMethodField()
    display_price = serializers.SerializerMethodField()
    category = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'size', 'description', 'quantity',
            'brand', 'thread_connection', 'thread_connection_2',
            'armament', 'seal', 'iadc', 'category',
            'images', 'main_image', 'price', 'display_price'
        ]

    def get_main_image(self, obj):
        request = self.context.get('request')
        if not request:
            return None

        try:
            # Используем prefetched images если доступно
            images = getattr(obj, 'images', [])
            if not images:
                images = list(obj.images.all())

            for img in images:
                if img.is_main and img.image:
                    return self.get_image_url(img, img.image)

            # Если нет главного, берём первое изображение
            for img in images:
                if img.image:
                    return self.get_image_url(img, img.image)

        except Exception as e:
            logger.exception(f"Error getting main image for product {obj.id}")

        return None

    def get_display_price(self, obj):
        return obj.display_price()


class CategoryProductsSerializer(CategorySerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta(CategorySerializer.Meta):
        fields = CategorySerializer.Meta.fields + ['products']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['phone', 'email', 'comment', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        total = 0

        for item_data in items_data:
            product = item_data['product']
            price = product.price if product.price else 0
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                price=price
            )
            total += price * item_data['quantity']

        order.total = total
        order.save()
        return order


class SaleItemImageSerializer(serializers.ModelSerializer, BaseImageSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = SaleItemImage
        fields = ['id', 'image_url', 'is_main', 'order', 'sale_item']
        extra_kwargs = {'sale_item': {'required': True}}

    def get_image_url(self, obj):
        return self.get_image_url(obj, obj.image) if hasattr(self, 'get_image_url') else None


class SaleItemSerializer(serializers.ModelSerializer, BaseImageSerializer):
    main_image = serializers.SerializerMethodField()
    images = SaleItemImageSerializer(many=True, read_only=True)

    class Meta:
        model = SaleItem
        fields = [
            'id', 'title', 'slug', 'description',
            'old_price', 'new_price', 'is_active',
            'created_at', 'main_image', 'images'
        ]
        read_only_fields = ['slug', 'created_at']

    def get_main_image(self, obj):
        try:
            # Используем prefetched images если доступно
            images = getattr(obj, 'images', [])
            if not images:
                images = list(obj.images.all())

            for img in images:
                if img.is_main and img.image:
                    return self.get_image_url(img, img.image)

            # Если нет главного, берём первое изображение
            for img in images:
                if img.image:
                    return self.get_image_url(img, img.image)

        except Exception as e:
            logger.exception(f"Error getting main image for sale item {obj.id}")

        return None

