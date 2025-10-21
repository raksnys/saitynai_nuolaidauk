from django.core.management.base import BaseCommand
import json
from catalog.models import Product, Category, Brand, Discount, Store
from decimal import Decimal, InvalidOperation
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

        # helper to parse offer date strings like '2025/10/20' or '2025-10-20'
        def _parse_offer_date(date_str, is_end=False):
            if not date_str:
                return None
            if isinstance(date_str, (int, float)):
                # Unexpected numeric value
                return None
            s = str(date_str).strip()
            dt = None
            for fmt in ("%Y/%m/%d", "%Y-%m-%d"):
                try:
                    dt = datetime.datetime.strptime(s, fmt)
                    break
                except ValueError:
                    continue
            if not dt:
                return None
            # If end datetime, set to end-of-day
            if is_end:
                dt = dt.replace(hour=23, minute=59, second=59)
            # Make timezone-aware in current timezone if naive
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt, timezone.get_current_timezone())
            return dt

        for item in data:
            if not item.get('category'):
                self.stdout.write(self.style.WARNING(f"Skipping product with no category: {item.get('name', 'Unknown name')}"))
                continue

            if not item.get('price'):
                self.stdout.write(self.style.WARNING(f"Skipping product with no price: {item.get('name', 'Unknown name')}"))
                continue

            category, _ = Category.objects.get_or_create(name=item['category'])

            product, created = Product.objects.update_or_create(
                external_id=item.get('id'),
                brand=brand,
                defaults={
                    'name': item['name'],
                    'category': category,
                    'price': item['price'],
                    'photo_url': item['photo_url'],
                    'store': None,
                    'description': item.get('description', None),
                }
            )

            # Allow both keys: 'discount_price' and 'discounted_price'
            discounted_val = item.get('discount_price', item.get('discounted_price'))
            if discounted_val is not None:
                try:
                    price_decimal = Decimal(str(item['price']))
                    discounted_decimal = Decimal(str(discounted_val))
                    discount_value = price_decimal - discounted_decimal
                except (InvalidOperation, TypeError):
                    self.stdout.write(self.style.WARNING(f"Could not calculate discount for product {product.name} due to invalid price/discount value."))
                    discount_value = Decimal('0')

                if discount_value > 0:
                    discount, _ = Discount.objects.update_or_create(
                        name=f"{product.name} Discount",
                        product=product,
                        defaults={
                            'discount_type': Discount.FIXED,
                            'value': discount_value,
                            'target_type': Discount.TARGET_PRODUCT,
                            # Parse optional offer dates like "2025/10/20" or "2025-10-20"
                            'starts_at': _parse_offer_date(item.get('offer_start_date'), is_end=False),
                            'ends_at': _parse_offer_date(item.get('offer_end_date'), is_end=True),
                            'status': Discount.DiscountStatus.APPROVED,
                            'brand': brand,
                        }
                    )
                    self.stdout.write(self.style.SUCCESS(f'Successfully created/updated product "{product.name}" with discount'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Successfully created/updated product "{product.name}"'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Successfully created/updated product "{product.name}"'))
