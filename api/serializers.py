from rest_framework import serializers
from .models import ContactMessage, Employee, Category, Product, OrderItem, Order, SaleItem, SaleItemImage, ProductImage


class BaseImageSerializer:
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        request = self.context.get('request')
        image_field = getattr(obj, 'photo', None) or getattr(obj, 'image', None)

        if image_field and request:
            try:
                return request.build_absolute_uri(image_field.url)
            except ValueError:
                return None
        return None


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'


class EmployeeSerializer(BaseImageSerializer, serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'


class CategorySerializer(BaseImageSerializer, serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image_url']


class ProductImageSerializer(BaseImageSerializer, serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'is_main', 'order', 'product']


class ProductSerializer(BaseImageSerializer, serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    main_image = serializers.SerializerMethodField()
    category = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'size', 'description', 'quantity',
            'brand', 'thread_connection', 'thread_connection_2',
            'armament', 'seal', 'iadc', 'category',
            'images', 'main_image', 'price'
        ]

    def get_main_image(self, obj):
        request = self.context.get('request')
        if not request:
            return None

        images = getattr(obj, 'prefetched_images', None) or obj.images.all()

        main_image = next((img for img in images if img.is_main), None)
        if not main_image and images:
            main_image = images[0]

        if main_image:
            return self.get_image_url(main_image)

        return None


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


class SaleItemImageSerializer(BaseImageSerializer, serializers.ModelSerializer):
    class Meta:
        model = SaleItemImage
        fields = ['id', 'image_url', 'is_main', 'order', 'sale_item']
        extra_kwargs = {'sale_item': {'required': True}}


class SaleItemSerializer(BaseImageSerializer, serializers.ModelSerializer):
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
        main_image = obj.images.filter(is_main=True).first()
        if main_image:
            return self.get_image_url(main_image)
        return None


