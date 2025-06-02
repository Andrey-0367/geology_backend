from django.contrib import admin
from .models import Position, Employee, Category, Product


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    search_fields = ('name',)
    list_editable = ('order',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'created_at')
    search_fields = ('full_name', 'bio')
    list_filter = ('is_active', 'positions')
    filter_horizontal = ('positions',)
    list_editable = ('is_active',)


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
