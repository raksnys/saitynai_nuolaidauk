from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """Abstract base class with created/updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Brand(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Category(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Store(TimeStampedModel):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="stores")
    nickname = models.CharField(
        max_length=255,
        help_text="Optional label to distinguish individual store locations.",
        blank=True,
    )
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default="Lithuania")

    class Meta:
        ordering = ["brand__name", "city", "nickname"]
        unique_together = ("brand", "address_line1", "postal_code")

    def __str__(self) -> str:
        base = f"{self.brand.name}"
        if self.nickname:
            base = f"{base} - {self.nickname}"
        return base


class Discount(TimeStampedModel):
    PERCENTAGE = "percentage"
    FIXED = "fixed"
    DISCOUNT_TYPE_CHOICES = [
        (PERCENTAGE, "Percentage"),
        (FIXED, "Fixed amount"),
    ]

    TARGET_PRODUCT = "product"
    TARGET_CATEGORY = "category"
    TARGET_BRAND = "brand"
    TARGET_TYPE_CHOICES = [
        (TARGET_PRODUCT, "Product"),
        (TARGET_CATEGORY, "Category"),
        (TARGET_BRAND, "Brand"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    target_type = models.CharField(max_length=20, choices=TARGET_TYPE_CHOICES)
    brand = models.ForeignKey(
        Brand,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="discounts",
    )
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="discounts",
    )
    product = models.ForeignKey(
        "Product",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="discount_rules",
    )
    starts_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(discount_type="percentage", value__lte=100)
                | models.Q(discount_type="fixed"),
                name="discount_percentage_max_100",
            )
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        target_map = {
            self.TARGET_BRAND: self.brand,
            self.TARGET_CATEGORY: self.category,
            self.TARGET_PRODUCT: self.product,
        }
        target = target_map.get(self.target_type)
        if target is None:
            raise ValidationError("Discount target does not match selected scope.")

        # Ensure other targets are empty
        for scope, fk in target_map.items():
            if scope != self.target_type and fk is not None:
                raise ValidationError("Only one discount target may be set.")

        if self.discount_type == self.PERCENTAGE and not (0 < self.value <= 100):
            raise ValidationError("Percentage discounts must be between 0 and 100.")
        if self.discount_type == self.FIXED and self.value <= 0:
            raise ValidationError("Fixed amount discounts must be greater than zero.")
        if self.ends_at and self.ends_at <= self.starts_at:
            raise ValidationError("Discount end date must be after the start date.")


class Product(TimeStampedModel):
    PER_PIECE = "per_piece"
    PER_KILOGRAM = "per_kilogram"
    PRICE_UNIT_CHOICES = [
        (PER_PIECE, "Per piece"),
        (PER_KILOGRAM, "Per kilogram"),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="products")
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    price_unit = models.CharField(max_length=20, choices=PRICE_UNIT_CHOICES, default=PER_PIECE)
    weight = models.DecimalField(max_digits=8, decimal_places=3, validators=[MinValueValidator(0)])
    discounts = models.ManyToManyField(
        "Discount",
        through="ProductDiscountHistory",
        related_name="products",
        blank=True,
    )

    class Meta:
        ordering = ["name"]
        unique_together = ("store", "name")

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        if self.brand != self.store.brand:
            raise ValidationError("Product brand must match the brand of the store it belongs to.")


class ProductDiscountHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="discount_history")
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, related_name="product_history")
    applied_at = models.DateTimeField(auto_now_add=True)
    removed_at = models.DateTimeField(null=True, blank=True)
    applied_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Snapshot of the product price when the discount was applied.",
    )

    class Meta:
        ordering = ["-applied_at"]
        verbose_name_plural = "product discount history"

    def __str__(self) -> str:
        return f"{self.discount} on {self.product} (@ {self.applied_at:%Y-%m-%d})"

    @property
    def is_active(self) -> bool:
        return self.removed_at is None or self.removed_at > timezone.now()
