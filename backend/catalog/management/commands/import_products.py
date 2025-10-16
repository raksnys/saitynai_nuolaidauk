from django.core.management.base import BaseCommand
import json
from catalog.models import Product, Category, Brand, Discount, Store
from decimal import Decimal
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Import products from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='The JSON file to import')
        parser.add_argument('brand_name', type=str, help='The brand name for the products')

    def handle(self, *args, **options):
        json_file_path = options['json_file']
        brand_name = options['brand_name']

        brand, _ = Brand.objects.get_or_create(name=brand_name)

        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            if not item.get('category'):
                self.stdout.write(self.style.WARNING(f"Skipping product with no category: {item.get('name', 'Unknown name')}"))
                continue

            category, _ = Category.objects.get_or_create(name=item['category'])

            product, created = Product.objects.update_or_create(
                external_id=item.get('id'),
                brand=brand,
                defaults={
                    'name': item['name'],
                    'category': category,
                    'price': Decimal(item['price']),
                    'photo_url': item['photo_url'],
                    'store': None,
                }
            )

            if 'discount_price' in item and item['discount_price'] is not None:
                discount_value = Decimal(item['price']) - Decimal(item['discount_price'])
                if discount_value > 0:
                    discount, _ = Discount.objects.update_or_create(
                        name=f"{product.name} Discount",
                        product=product,
                        defaults={
                            'discount_type': Discount.FIXED,
                            'value': discount_value,
                            'target_type': Discount.TARGET_PRODUCT,
                            'starts_at': timezone.now(),
                            'ends_at': datetime.datetime(2025, 10, 20, tzinfo=datetime.timezone.utc),
                            'status': Discount.STATUS_APPROVED,
                            'brand': brand,
                        }
                    )
                    self.stdout.write(self.style.SUCCESS(f'Successfully created/updated product "{product.name}" with discount'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Successfully created/updated product "{product.name}"'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Successfully created/updated product "{product.name}"'))
