from django.core.management.base import BaseCommand
from api.models import Product  # Измените импорт на ваше приложение


class Command(BaseCommand):
    help = 'Fix product prices before making price required'

    def handle(self, *args, **kwargs):
        # Установите минимальную цену для товаров без цены
        updated_null = Product.objects.filter(price__isnull=True).update(price=0.01)

        # Исправьте нулевые цены
        updated_zero = Product.objects.filter(price=0).update(price=0.01)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully fixed {updated_null + updated_zero} product prices. '
                f'Null prices: {updated_null}, Zero prices: {updated_zero}'
            )
        )