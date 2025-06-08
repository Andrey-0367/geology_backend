import os

from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import MinValueValidator


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
    name = models.CharField("Название категории", max_length=255)
    image = models.ImageField("Изображение категории", upload_to='categories/', blank=True, null=True)
    slug = models.SlugField("URL-адрес", max_length=255, unique=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    is_active = models.BooleanField("Активная", default=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Категория"
    )
    name = models.CharField("Название товара", max_length=255)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    image = models.ImageField("Изображение товара", upload_to='products/')
    description = models.TextField("Описание товара", blank=True)
    slug = models.SlugField("URL-адрес", max_length=255, unique=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    is_active = models.BooleanField("Активный", default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('completed', 'Завершен'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.PROTECT
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"


class SaleItem(models.Model):
    title = models.CharField("Название", max_length=255)
    slug = models.SlugField("URL-адрес", max_length=255, unique=True)
    description = models.TextField("Описание")
    old_price = models.DecimalField(
        "Старая цена",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    new_price = models.DecimalField(
        "Новая цена",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
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
