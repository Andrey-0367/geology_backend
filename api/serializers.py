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
    image_url = serializers.SerializerMethodField()
    is_svg = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'image_url', 'is_svg']

    def get_image_url(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None

    def get_is_svg(self, obj):
        return obj.image.name.endswith('.svg') if obj.image else False


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    is_svg = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'is_svg', 'is_main', 'order', 'product']

    def get_image_url(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None

    def get_is_svg(self, obj):
        return obj.image.name.endswith('.svg') if obj.image else False


class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()  # Изменено!
    main_image = serializers.SerializerMethodField()
    display_price = serializers.SerializerMethodField()
    category_id = serializers.IntegerField(source='category.id', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'size', 'description', 'quantity',
            'brand', 'thread_connection', 'thread_connection_2',
            'armament', 'seal', 'iadc',
            'images', 'main_image', 'price', 'display_price',
            'category_id'
        ]

    def get_images(self, obj):  # Новый метод!
        images = obj.images.all()
        serializer = ProductImageSerializer(
            images,
            many=True,
            context=self.context
        )
        return serializer.data

    def get_image_url(self, obj):
        if obj.image:
            try:
                if obj.image.storage.exists(obj.image.name):
                    return self.context['request'].build_absolute_uri(obj.image.url)
                return None
            except (ValueError, AttributeError):
                return None
        return None

    def get_is_svg(self, obj):
        try:
            return obj.image.name.endswith('.svg') if obj.image else False
        except (AttributeError, ValueError):
            return False

    def get_display_price(self, obj):
        return obj.display_price()


class CategoryProductsSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()  # Изменено!
    image_url = serializers.SerializerMethodField()
    is_svg = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'image_url', 'is_svg', 'products']

    def get_products(self, obj):
        products = obj.products.all().prefetch_related('images')
        serializer = ProductSerializer(
            products,
            many=True,
            context=self.context
        )
        return serializer.data

    def get_image_url(self, obj):
        if obj.image:
            try:
                if obj.image.storage.exists(obj.image.name):
                    return self.context['request'].build_absolute_uri(obj.image.url)
                return None
            except (ValueError, AttributeError):
                return None
        return None

    def get_is_svg(self, obj):
        try:
            return obj.image.name.endswith('.svg') if obj.image else False
        except (AttributeError, ValueError):
            return False


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


