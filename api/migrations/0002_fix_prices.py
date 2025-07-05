from django.db import migrations


def fix_prices(apps, schema_editor):
    Product = apps.get_model('api', 'Product')
    # Установить 0.01 для всех товаров без цены
    Product.objects.filter(price__isnull=True).update(price=0.01)
    # Исправить нулевые цены
    Product.objects.filter(price=0).update(price=0.01)


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(fix_prices),
    ]