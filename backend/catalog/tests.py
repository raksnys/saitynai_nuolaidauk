from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from .models import (
    Brand,
    Category,
    Discount,
    Product,
    ProductDiscountHistory,
    Store,
)


class CatalogModelsTests(TestCase):
    def setUp(self):
        self.brand = Brand.objects.create(name="Rimi")
        self.category = Category.objects.create(name="Bakery")
        self.store = Store.objects.create(
            brand=self.brand,
            nickname="City Center",
            address_line1="Konstitucijos pr. 7",
            city="Vilnius",
            country="Lithuania",
        )

    def test_product_brand_matches_store_brand(self):
        product = Product(
            store=self.store,
            brand=self.brand,
            category=self.category,
            name="Batonas",
            price=Decimal("2.50"),
            price_unit=Product.PER_PIECE,
            weight=Decimal("0.400"),
        )
        # Should save without issue when brands align
        product.full_clean()
        product.save()

        other_brand = Brand.objects.create(name="Maxima")
        invalid_product = Product(
            store=self.store,
            brand=other_brand,
            category=self.category,
            name="Wrong brand",
            price=Decimal("1.99"),
            price_unit=Product.PER_PIECE,
            weight=Decimal("0.300"),
        )
        with self.assertRaises(ValidationError):
            invalid_product.full_clean()

    def test_discount_scope_validation(self):
        discount = Discount(
            name="Bakery Week",
            discount_type=Discount.PERCENTAGE,
            value=Decimal("15"),
            target_type=Discount.TARGET_CATEGORY,
            category=self.category,
        )
        discount.full_clean()
        discount.save()

        bad_discount = Discount(
            name="Broken",
            discount_type=Discount.FIXED,
            value=Decimal("2.00"),
            target_type=Discount.TARGET_PRODUCT,
            category=self.category,
        )
        with self.assertRaises(ValidationError):
            bad_discount.full_clean()

    def test_product_discount_history_records_snapshot(self):
        product = Product.objects.create(
            store=self.store,
            brand=self.brand,
            category=self.category,
            name="Sourdough",
            price=Decimal("3.50"),
            price_unit=Product.PER_PIECE,
            weight=Decimal("0.500"),
        )
        discount = Discount.objects.create(
            name="Sourdough promo",
            discount_type=Discount.FIXED,
            value=Decimal("0.50"),
            target_type=Discount.TARGET_PRODUCT,
            product=product,
        )
        history = ProductDiscountHistory.objects.create(
            product=product,
            discount=discount,
            applied_price=product.price,
        )
        self.assertIsNone(history.removed_at)
        self.assertTrue(history.is_active)

        history.removed_at = timezone.now()
        history.save()
        history.refresh_from_db()
        self.assertFalse(history.is_active)
