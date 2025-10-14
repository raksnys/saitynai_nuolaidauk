from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    Brand,
    Category,
    Discount,
    Product,
    ProductDiscountHistory,
    Store,
)

User = get_user_model()


class CatalogModelsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="modeltest@example.com", password="password")
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
        now = timezone.now()
        discount = Discount(
            name="Bakery Week",
            discount_type=Discount.PERCENTAGE,
            value=Decimal("15"),
            target_type=Discount.TARGET_CATEGORY,
            category=self.category,
            submitted_by=self.user,
            starts_at=now,
            ends_at=now + timezone.timedelta(days=1),
        )
        discount.full_clean()
        discount.save()

        bad_discount = Discount(
            name="Broken",
            discount_type=Discount.FIXED,
            value=Decimal("2.00"),
            target_type=Discount.TARGET_PRODUCT,
            category=self.category,
            submitted_by=self.user,
            starts_at=now,
            ends_at=now + timezone.timedelta(days=1),
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
        now = timezone.now()
        discount = Discount.objects.create(
            name="Sourdough promo",
            discount_type=Discount.FIXED,
            value=Decimal("0.50"),
            target_type=Discount.TARGET_PRODUCT,
            product=product,
            submitted_by=self.user,
            starts_at=now,
            ends_at=now + timezone.timedelta(days=1),
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


class UserDiscountAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="password123"
        )
        self.other_user = User.objects.create_user(
            email="otheruser@example.com", password="password123"
        )
        self.client.force_authenticate(user=self.user)

        self.brand = Brand.objects.create(name="Test Brand")
        self.category = Category.objects.create(name="Test Category")
        self.store = Store.objects.create(
            brand=self.brand,
            address_line1="123 Test St",
            city="Testville",
        )
        self.product = Product.objects.create(
            store=self.store,
            brand=self.brand,
            category=self.category,
            name="Test Product",
            price=Decimal("10.00"),
            weight=Decimal("0.500"),  # Added missing weight
        )
        self.list_create_url = reverse("catalog:user-discount-list-create")

    def test_list_user_discounts(self):
        """
        Ensure GET request returns only the authenticated user's discounts.
        """
        # Discount for the authenticated user
        Discount.objects.create(
            name="My Discount",
            discount_type=Discount.FIXED,
            value=5,
            target_type=Discount.TARGET_PRODUCT,
            product=self.product,
            submitted_by=self.user,
            starts_at=timezone.now(),
            ends_at=timezone.now() + timezone.timedelta(days=1),
        )
        # Discount for another user
        Discount.objects.create(
            name="Other's Discount",
            discount_type=Discount.PERCENTAGE,
            value=10,
            target_type=Discount.TARGET_CATEGORY,
            category=self.category,
            submitted_by=self.other_user,
            starts_at=timezone.now(),
            ends_at=timezone.now() + timezone.timedelta(days=1),
        )

        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "My Discount")

    def test_create_discount_for_existing_product(self):
        """
        Ensure user can create a discount for an existing product.
        """
        data = {
            "name": "Product Discount",
            "discount_type": Discount.FIXED,
            "value": "2.50",
            "starts_at": timezone.now(),
            "ends_at": timezone.now() + timezone.timedelta(days=5),
            "store_id": self.store.id,
            "product_id": self.product.id,
        }
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        discount = Discount.objects.get(id=response.data["id"])
        self.assertEqual(discount.submitted_by, self.user)
        self.assertEqual(discount.status, Discount.STATUS_IN_REVIEW)
        self.assertEqual(discount.target_type, Discount.TARGET_PRODUCT)
        self.assertEqual(discount.product, self.product)

    def test_create_discount_with_new_product(self):
        """
        Ensure user can create a discount and a new product simultaneously.
        """
        self.assertEqual(Product.objects.count(), 1)
        data = {
            "name": "New Item Sale",
            "discount_type": Discount.PERCENTAGE,
            "value": "20",
            "starts_at": timezone.now(),
            "ends_at": timezone.now() + timezone.timedelta(days=10),
            "store_id": self.store.id,
            "new_product": {
                "name": "Brand New Gadget",
                "brand": self.brand.name,
                "category": self.category.name,
                "price": "99.99",
                "price_unit": Product.PER_PIECE,
                "weight": "0.500",  # Added missing weight
            },
        }
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(Discount.objects.count(), 1)

        new_product = Product.objects.get(name="Brand New Gadget")
        discount = Discount.objects.get(id=response.data["id"])
        self.assertEqual(discount.product, new_product)
        self.assertEqual(discount.status, Discount.STATUS_IN_REVIEW)

    def test_create_discount_validation_error(self):
        """
        Ensure validation fails if both product_id and new_product are provided.
        """
        data = {
            "name": "Conflicting Discount",
            "discount_type": Discount.FIXED,
            "value": "1.00",
            "starts_at": timezone.now(),
            "ends_at": timezone.now() + timezone.timedelta(days=2),
            "store_id": self.store.id,
            "product_id": self.product.id,  # Conflict
            "new_product": {  # Conflict
                "name": "Another Gadget",
                "brand": self.brand.name,
                "category": self.category.name,
                "price": "50.00",
                "weight": "0.200", # Add weight to avoid a different validation error
            },
        }
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertIn("You must specify exactly one of", response.data["non_field_errors"][0])

    def test_effective_status_property(self):
        """
        Test the logic of the `effective_status` property on the Discount model.
        """
        now = timezone.now()
        discount = Discount.objects.create(
            name="Status Test",
            discount_type=Discount.FIXED,
            value=1,
            target_type=Discount.TARGET_PRODUCT,
            product=self.product,
            submitted_by=self.user,
            starts_at=now + timezone.timedelta(days=1),
            ends_at=now + timezone.timedelta(days=2),
        )

        # Default status is IN_REVIEW
        self.assertEqual(discount.effective_status, "IN_REVIEW")

        # Status: DENIED
        discount.status = Discount.STATUS_DENIED
        discount.save()
        self.assertEqual(discount.effective_status, "DENIED")

        # Status: APPROVED (future start date)
        discount.status = Discount.STATUS_APPROVED
        discount.save()
        self.assertEqual(discount.effective_status, "APPROVED")

        # Status: IN_ACTION (start date is in the past, end date in the future)
        discount.starts_at = now - timezone.timedelta(days=1)
        discount.save()
        self.assertEqual(discount.effective_status, "IN_ACTION")

        # Status: ENDED (end date is in the past)
        discount.ends_at = now - timezone.timedelta(minutes=1)
        discount.save()
        self.assertEqual(discount.effective_status, "ENDED")
