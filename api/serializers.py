from rest_framework import serializers

from geology import settings
from .models import ContactMessage, Employee, Category, Product, Order, SaleItem, SaleItemImage, \
    ProductImage


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


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'status')


class SaleItemImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = SaleItemImage
        fields = '__all__'

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None


class SaleItemSerializer(serializers.ModelSerializer):
    main_image_url = serializers.SerializerMethodField()

    class Meta:
        model = SaleItem
        fields = '__all__'

    def get_main_image_url(self, obj):
        # Просто ищем главное изображение среди связанных изображений
        main_image = obj.images.filter(is_main=True).first()

        if main_image and main_image.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(main_image.image.url)
        return None
