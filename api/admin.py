from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
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

    class Meta:
        verbose_name = _('Сотрудник')
        verbose_name_plural = _('Сотрудники')


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'preview']
    readonly_fields = ['preview']
    verbose_name = _('Изображение продукта')
    verbose_name_plural = _('Изображения продуктов')

    def preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 100px;"/>')
        return "-"

    preview.short_description = _("Предпросмотр")


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
        (_('Дополнительные характеристики'), {
            'fields': ('brand', 'thread_connection', 'thread_connection_2', 'armament', 'seal', 'iadc'),
            'classes': ('collapse',)
        }),
    )

    class Meta:
        verbose_name = _('Продукт')
        verbose_name_plural = _('Продукты')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'image_preview']
    readonly_fields = ['image_preview']
    search_fields = ['name']

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" height="100" />')
        return _("Нет изображения")

    image_preview.short_description = _("Превью")

    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'image_preview', 'is_main', 'order']
    list_editable = ['is_main', 'order']
    list_filter = ['product', 'is_main']
    search_fields = ['product__name']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" height="100" />')
        return _("Нет изображения")

    image_preview.short_description = _("Превью")

    class Meta:
        verbose_name = _('Изображение продукта')
        verbose_name_plural = _('Изображения продуктов')


@admin.register(SaleItemImage)
class SaleItemImageAdmin(admin.ModelAdmin):
    list_display = ('sale_item', 'is_main', 'order')
    list_editable = ('is_main', 'order')
    list_filter = ('sale_item', 'is_main')
    search_fields = ('sale_item__title',)
    fields = ('sale_item', 'image', 'is_main', 'order')

    class Meta:
        verbose_name = _('Изображение товара распродажи')
        verbose_name_plural = _('Изображения товаров распродажи')


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'old_price', 'new_price', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    fields = ('title', 'slug', 'description', 'old_price', 'new_price', 'is_active')

    class Meta:
        verbose_name = _('Товар распродажи')
        verbose_name_plural = _('Товары распродажи')
        
