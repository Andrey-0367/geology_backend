from django.contrib import admin
from django.utils.html import format_html

from .models import Employee, Category, Product, SaleItemImage, SaleItem, ProductImage


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'positions', 'created_at')
    search_fields = ('full_name', 'positions')
    list_filter = ('created_at',)

    fieldsets = (
        (None, {
            'fields': ('full_name', 'photo', 'positions', 'bio')
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_plural', 'slug', 'image_preview')
    search_fields = ('name_plural',)
    prepopulated_fields = {'slug': ('name_plural',)}

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "Нет изображения"

    image_preview.short_description = "Превью"
    readonly_fields = ('image_preview',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'order', 'preview')
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "Нет изображения"

    preview.short_description = "Превью"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name_singular',
        'marking',
        'category',
        'price',
        'stock_quantity',
        'created_at',
    )
    list_filter = ('category', 'created_at')
    search_fields = (
        'name_singular',
        'marking',
        'description',
        'category__name_plural'
    )
    date_hierarchy = 'created_at'
    raw_id_fields = ('category',)
    inlines = (ProductImageInline,)
    fieldsets = (
        (None, {
            'fields': (
                'category',
                'name_singular',
                'marking',
                'price',
                'stock_quantity'
            )
        }),
        ('Описание', {
            'fields': ('description', 'specifications')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'order', 'preview')
    list_editable = ('order',)
    raw_id_fields = ('product',)

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "Нет изображения"

    preview.short_description = "Превью"


@admin.register(SaleItemImage)
class SaleItemImageAdmin(admin.ModelAdmin):
    list_display = ('sale_item', 'is_main', 'order')
    list_editable = ('is_main', 'order')
    list_filter = ('sale_item', 'is_main')
    search_fields = ('sale_item__title',)
    fields = ('sale_item', 'image', 'is_main', 'order')


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'old_price', 'new_price', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    fields = ('title', 'slug', 'description', 'old_price', 'new_price', 'is_active')
