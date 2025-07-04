from rest_framework import serializers
from .models import ContactMessage, Employee, Category, Product, OrderItem, Order, SaleItem, SaleItemImage, \
    ProductImage, logger


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
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo.url)
        return None


class CategorySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    is_svg = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'image_url', 'is_svg']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None

    def get_is_svg(self, obj):
        if obj.image:
            return obj.image.name.endswith('.svg') if obj.image else False
        return False


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    is_svg = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'is_svg', 'is_main', 'order', 'product']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None

    def get_is_svg(self, obj):
        if obj.image:
            return obj.image.name.endswith('.svg') if obj.image else False
        return False


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    main_image = serializers.SerializerMethodField()
    image_urls = serializers.SerializerMethodField()
    display_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'size', 'description', 'quantity',
            'brand', 'thread_connection', 'thread_connection_2',
            'armament', 'seal', 'iadc', 'category',
            'images', 'main_image', 'image_urls',  'price', 'display_price'
        ]

    def get_main_image(self, obj):
        if not hasattr(obj, 'images'):
            return None

        main_image = obj.images.filter(is_main=True).first()
        if main_image and main_image.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(main_image.image.url)

        first_image = obj.images.first()
        if first_image and first_image.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_image.image.url)

        return None

    def get_image_urls(self, obj):
        if not hasattr(obj, 'images') or not obj.images.exists():
            return []

        urls = []
        for img in obj.images.all():
            if img.image:
                request = self.context.get('request')
                if request:
                    urls.append(request.build_absolute_uri(img.image.url))
        return urls

    def get_display_price(self, obj):
        return obj.display_price()


class CategoryProductsSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()
    is_svg = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'image_url', 'is_svg', 'products']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None

    def get_is_svg(self, obj):
        if obj.image:
            return obj.image.name.endswith('.svg') if obj.image else False
        return False


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all()
    )

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'phone', 'email', 'comment',
            'company', 'country', 'zip_code', 'region', 'city', 'address',
            'delivery_method', 'agreed_to_terms', 'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        total = 0

        for item_data in items_data:
            product = item_data['product']

            # Автоматически устанавливаем цену из продукта
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                price=product.price  # Ключевое изменение
            )
            total += product.price * item_data['quantity']

        order.total = total
        order.save()

        # Отправка email (с обработкой ошибок)
        try:
            order.send_confirmation_email()
        except Exception as e:
            logger.error(f"Ошибка отправки email: {str(e)}")

        return order


class SaleItemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItemImage
        fields = ['id', 'image', 'is_main', 'order', 'sale_item']
        extra_kwargs = {
            'sale_item': {'required': True}
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

    def get_main_image(self, obj):
        main_image = obj.images.filter(is_main=True).first()
        if main_image and main_image.image:
            return main_image.image.url
        return None

