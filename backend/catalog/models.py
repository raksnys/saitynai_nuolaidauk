from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.conf import settings
from decimal import Decimal


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

    class DiscountStatus(models.TextChoices):
        IN_REVIEW = "in_review", "In Review"
        APPROVED = "approved", "Approved"
        DENIED = "denied", "Denied"

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
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
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    status = models.CharField(
        max_length=20, choices=DiscountStatus.choices, default=DiscountStatus.IN_REVIEW
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="submitted_discounts",
    )

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

    @property
    def effective_status(self) -> str:
        """Returns the calculated status based on current time."""
        if self.status == self.DiscountStatus.IN_REVIEW:
            return "IN_REVIEW"
        if self.status == self.DiscountStatus.DENIED:
            return "DENIED"
        if self.status == self.DiscountStatus.APPROVED:
            now = timezone.now()
            if self.ends_at < now:
                return "ENDED"
            if self.starts_at > now:
                return "APPROVED"
            return "IN_ACTION"
        return self.status.upper()

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

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="products", null=True, blank=True)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        related_name="products",
        null=True,
        blank=True,
    )
    external_id = models.CharField(max_length=255, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    photo_url = models.URLField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0'))], null=True, blank=True)
    price_unit = models.CharField(max_length=20, choices=PRICE_UNIT_CHOICES, default=PER_PIECE, null=True, blank=True)
    weight = models.DecimalField(max_digits=8, decimal_places=3, validators=[MinValueValidator(Decimal('0'))], null=True, blank=True)
    discounts = models.ManyToManyField(
        "Discount",
        through="ProductDiscountHistory",
        related_name="products",
        blank=True,
    )

    class Meta:
        ordering = ["name"]
        unique_together = ("brand", "external_id")

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        if self.store is None:
            return
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
    validators=[MinValueValidator(Decimal('0'))],
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


class WishlistItem(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist_items")
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="wishlisted_by")

    class Meta:
        unique_together = ("user", "product")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user_id} -> {self.product_id}"


class Report(TimeStampedModel):
    """A user report targeting either a product or a discount.
    Requirements:
    - If reporting a product: a single reason must be selected (name/photo/price)
    - If reporting a discount: an image (base64) must be provided
    - Both must include a textual description
    - Moderators/Admins can change status from REPORTED to ACCEPTED or DENIED
    """

    class ReportStatus(models.TextChoices):
        REPORTED = "REPORTED", "Reported"
        ACCEPTED = "ACCEPTED", "Accepted"
        DENIED = "DENIED", "Denied"

    PRODUCT_REASON_NAME = "name"
    PRODUCT_REASON_PHOTO = "photo"
    PRODUCT_REASON_PRICE = "price"
    PRODUCT_REASON_CHOICES = [
        (PRODUCT_REASON_NAME, "Name"),
        (PRODUCT_REASON_PHOTO, "Photo"),
        (PRODUCT_REASON_PRICE, "Price"),
    ]

    # Target: exactly one of product or discount
    product = models.ForeignKey(
        "Product", null=True, blank=True, on_delete=models.CASCADE, related_name="reports"
    )
    discount = models.ForeignKey(
        "Discount", null=True, blank=True, on_delete=models.CASCADE, related_name="reports"
    )

    # For product reports, a single reason is selected
    product_reason = models.CharField(max_length=16, choices=PRODUCT_REASON_CHOICES, null=True, blank=True)

    # For discount reports, an image in base64 is required
    discount_image_base64 = models.TextField(blank=True)

    # Free-form description required for both
    description = models.TextField()

    # Workflow status
    status = models.CharField(max_length=16, choices=ReportStatus.choices, default=ReportStatus.REPORTED)

    # Reporter
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reports_submitted",
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            # XOR: exactly one of product or discount must be set
            models.CheckConstraint(
                name="report_exactly_one_target",
                check=(
                    (models.Q(product__isnull=False) & models.Q(discount__isnull=True))
                    | (models.Q(product__isnull=True) & models.Q(discount__isnull=False))
                ),
            )
        ]

    def clean(self) -> None:
        if bool(self.product) == bool(self.discount):
            raise ValidationError("Exactly one of product or discount must be provided.")
        if self.product and not self.product_reason:
            raise ValidationError("Product reports must include a product_reason.")
        if self.discount and not self.discount_image_base64:
            raise ValidationError("Discount reports must include a base64 image.")
        if not self.description:
            raise ValidationError("Description is required.")

    def __str__(self) -> str:
        target = f"product={self.product_id}" if self.product_id else f"discount={self.discount_id}"
        return f"Report({target}, status={self.status})"
