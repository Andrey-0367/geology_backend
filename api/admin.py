from django.contrib import admin
from .models import Employee, Category, Product, SaleItemImage, SaleItem


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
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


class SaleItemImageInline(admin.TabularInline):
    model = SaleItemImage
    extra = 1
    fields = ['image', 'is_main', 'order']
    readonly_fields = ['preview']

    def preview(self, instance):
        if instance.image:
            return f'<img src="{instance.image.url}" style="max-height: 100px;" />'
        return '-'

    preview.allow_tags = True


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'old_price', 'new_price', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [SaleItemImageInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'is_active')
        }),
        ('Цены', {
            'fields': ('old_price', 'new_price'),
        }),
    )


@admin.register(SaleItemImage)
class SaleItemImageAdmin(admin.ModelAdmin):
    list_display = ['sale_item', 'preview', 'is_main', 'order']
    list_editable = ['is_main', 'order']
    list_filter = ['sale_item', 'is_main']
    search_fields = ['sale_item__title']

    def preview(self, instance):
        if instance.image:
            return f'<img src="{instance.image.url}" style="max-height: 50px;" />'
        return '-'

    preview.allow_tags = True
