from django.contrib import admin
from django.utils.safestring import mark_safe

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


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'preview']
    readonly_fields = ['preview']

    def preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 100px;"/>')
        return "-"

    preview.short_description = "Предпросмотр"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'size', 'category', 'quantity']
    list_filter = ['category']
    search_fields = ['name', 'description']
    inlines = [ProductImageInline]

    fieldsets = (
        (None, {
            'fields': ('category', 'name', 'size', 'description', 'quantity')
        }),
        ('Дополнительные характеристики', {
            'fields': ('brand', 'thread_connection', 'thread_connection_2', 'armament', 'seal', 'iadc'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'preview']
    readonly_fields = ['preview']

    def preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 200px;"/>')
        return "-"

    preview.short_description = "Изображение"


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
