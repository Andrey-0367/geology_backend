from rest_framework import serializers
from .models import ContactMessage, Employee, Category, Product, OrderItem, Order, SaleItem, SaleItemImage, ProductImage


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
        if obj.photo:
            return self.context['request'].build_absolute_uri(obj.photo.url)
        return None


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'category',
            'name',
            'size',
            'description',
            'quantity',
            'brand',
            'thread_connection',
            'thread_connection_2',
            'armament',
            'seal',
            'iadc',
            'images'
        ]


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
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                price=product.price
            )
            total += product.price * item_data['quantity']

        order.total = total
        order.save()
        return order


class SaleItemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItemImage
        fields = ['id', 'image', 'is_main', 'order', 'sale_item']  # Оставляем sale_item
        extra_kwargs = {
            'sale_item': {'required': True}  # Явно указываем что поле обязательно
        }


class SaleItemSerializer(serializers.ModelSerializer):
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = SaleItem
        fields = [
            'id', 'title', 'slug', 'description',
            'old_price', 'new_price', 'is_active',
            'created_at', 'main_image'
        ]
        read_only_fields = ['slug', 'created_at']

    @staticmethod
    def get_main_image(obj):
        main_image = obj.images.filter(is_main=True).first()
        if main_image:
            return main_image.image.url
        return None
