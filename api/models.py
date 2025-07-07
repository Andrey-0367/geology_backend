from decimal import Decimal
import os

from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _


from .validators import validate_image_extension, validate_image_size, validate_svg_content

import logging
logger = logging.getLogger(__name__)


class ContactMessage(models.Model):
    email = models.EmailField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.email}"


class Employee(models.Model):
    full_name = models.CharField("Полное имя", max_length=255)
    photo = models.ImageField("Фото", upload_to='employees/', blank=True, null=True)
    positions = models.TextField("Должности", blank=True)
    bio = models.TextField("Биография", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.id:
            super().save(*args, **kwargs)

        if self.photo:
            ext = os.path.splitext(self.photo.name)[1]
            filename = f"{slugify(self.full_name)}-{self.id}{ext}"
            new_path = os.path.join('employees', filename)

            if self.photo.name != new_path:
                old_full_path = os.path.join(settings.MEDIA_ROOT, self.photo.name)
                new_full_path = os.path.join(settings.MEDIA_ROOT, new_path)

                os.makedirs(os.path.dirname(new_full_path), exist_ok=True)

                if os.path.exists(old_full_path):
                    os.rename(old_full_path, new_full_path)

                self.photo.name = new_path
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Команда"

    def __str__(self):
        return self.full_name


class Category(models.Model):
    name = models.CharField(_('Название'), max_length=255)
    image = models.FileField(
        _('Изображение'),
        upload_to='categories/',
        blank=True,
        null=True,
        validators=[
            validate_image_extension,
            validate_image_size,
            validate_svg_content
        ]
    )

    def image_preview(self):
        if self.image:
            if self.image.name.endswith('.svg'):
                return mark_safe(f'<img src="{self.image.url}" height="100" />')
            return mark_safe(f'<img src="{self.image.url}" height="100" />')
        return _("Нет изображения")

    image_preview.short_description = _("Превью")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('Категория')
    )
    name = models.CharField(_('Название'), max_length=255)
    size = models.CharField(_('Размер'), max_length=100, null=True, blank=True)
    description = models.TextField(_('Описание'))
    quantity = models.PositiveIntegerField(
        _('Количество'),
        default=0
    )
    price = models.DecimalField(
        _('Цена'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text=_('Цена в рублях. Минимальное значение: 0.01')
    )

    # Необязательные поля
    brand = models.CharField(_('Марка'), max_length=100, blank=True, null=True)
    thread_connection = models.CharField(_('Присоединительная резьба'), max_length=100, blank=True, null=True)
    thread_connection_2 = models.CharField(_('Присоединительная резьба 2'), max_length=100, blank=True, null=True)
    armament = models.CharField(_('Вооружение'), max_length=100, blank=True, null=True)
    seal = models.CharField(_('Уплотнение'), max_length=100, blank=True, null=True)
    iadc = models.CharField(_('IADC'), max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = _('Продукт')
        verbose_name_plural = _('Продукты')
        ordering = ['id']

    def __str__(self):
        return f"{self.name} ({self.size})" if self.size else self.name

    def clean(self):
        """Валидация перед сохранением"""
        if self.price <= 0:
            raise ValidationError({'price': 'Цена должна быть больше 0'})

    def save(self, *args, **kwargs):
        """Автоматическая валидация при сохранении"""
        self.full_clean()
        super().save(*args, **kwargs)

    def display_price(self):
        """Форматированное отображение цены"""
        formatted_price = format(self.price, ',.2f').replace(',', ' ')
        return f"{formatted_price} руб."


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        related_name='images',
        on_delete=models.CASCADE,
        verbose_name=_('Продукт')
    )
    image = models.FileField(
        _('Изображение'),
        upload_to='products/',
        validators=[
            validate_image_extension,
            validate_image_size,
            validate_svg_content
        ]
    )
    is_main = models.BooleanField(
        _('Главное изображение'),
        default=False,
        help_text=_('Используется как основное в списках товаров')
    )
    order = models.PositiveIntegerField(
        _('Порядок сортировки'),
        default=0
    )

    def image_preview(self):
        if self.image:
            if self.image.name.endswith('.svg'):
                return mark_safe(f'<img src="{self.image.url}" height="100" />')
            return mark_safe(f'<img src="{self.image.url}" height="100" />')
        return _("Нет изображения")
    image_preview.short_description = _("Превью")

    def __str__(self):
        return f"Изображение #{self.id} для {self.product.name if self.product else '?'}"

    class Meta:
        ordering = ['id']


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default='new')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    comment = models.TextField(blank=True)
    first_name = models.CharField("Имя", max_length=100)
    last_name = models.CharField("Фамилия", max_length=100)
    company = models.CharField("Компания", max_length=100, blank=True)
    country = models.CharField("Страна", max_length=100, default="Российская Федерация")
    zip_code = models.CharField("Индекс", max_length=20)
    region = models.CharField("Регион", max_length=100)
    city = models.CharField("Город", max_length=100)
    address = models.CharField("Адрес", max_length=255)
    delivery_method = models.CharField("Способ доставки", max_length=50)
    agreed_to_terms = models.BooleanField("Согласие", default=False)
    products = models.JSONField("Товары")  # Упрощаем хранение товаров

    def __str__(self):
        return f"Order #{self.id}"


class SaleItem(models.Model):
    title = models.CharField("Название", max_length=255)
    slug = models.SlugField("URL-адрес", max_length=255, unique=True)
    description = models.TextField("Описание")
    old_price = models.DecimalField(
        "Старая цена",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    new_price = models.DecimalField(
        "Новая цена",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    is_active = models.BooleanField("Активный", default=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Товар распродажи"
        verbose_name_plural = "Товары распродажи"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class SaleItemImage(models.Model):
    sale_item = models.ForeignKey(
        SaleItem,
        related_name='images',
        on_delete=models.CASCADE,
        verbose_name="Товар распродажи"
    )
    image = models.ImageField(
        "Изображение",
        upload_to='sale_items/'
    )
    is_main = models.BooleanField(
        "Главное изображение",
        default=False,
        help_text="Используется как основное в списках товаров"
    )
    order = models.PositiveIntegerField(
        "Порядок сортировки",
        default=0
    )

    class Meta:
        verbose_name = "Изображение товара распродажи"
        verbose_name_plural = "Изображения товаров распродажи"
        ordering = ['order']

    def __str__(self):
        return f"Изображение для {self.sale_item.title}"
