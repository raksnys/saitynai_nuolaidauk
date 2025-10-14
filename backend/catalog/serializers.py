from rest_framework import serializers
from .models import Product, Category, Discount, Store, Brand, ProductDiscountHistory
from django.utils import timezone


class UserDiscountListSerializer(serializers.ModelSerializer):
    """Serializer for listing user-submitted discounts with their status."""
    effective_status = serializers.CharField(read_only=True)

    class Meta:
        model = Discount
        fields = [
            "id",
            "name",
            "description",
            "target_type",
            "starts_at",
            "ends_at",
            "effective_status",
        ]


class UserProductCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a product within the discount submission."""
    brand = serializers.CharField()
    category = serializers.CharField()

    class Meta:
        model = Product
        fields = [
            "name",
            "brand",
            "category",
            "price",
            "price_unit",
            "weight",
            "description",
        ]


class UserDiscountCreateSerializer(serializers.ModelSerializer):
    """Serializer for users to submit a new discount for moderation."""
    store_id = serializers.IntegerField(write_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False)
    product_id = serializers.IntegerField(write_only=True, required=False)
    new_product = UserProductCreateSerializer(required=False, write_only=True)

    class Meta:
        model = Discount
        fields = [
            "id",  # Add id field
            "name",
            "description",
            "discount_type",
            "value",
            "starts_at",
            "ends_at",
            "store_id",
            "category_id",
            "product_id",
            "new_product",
        ]
        read_only_fields = ("id",)  # Mark id as read-only
        extra_kwargs = {
            'description': {'required': False}
        }

    def validate(self, data):
        """
        Validate that either an existing product/category is provided, or data for a new product.
        """
        has_product_id = "product_id" in data
        has_category_id = "category_id" in data
        has_new_product = "new_product" in data

        if not (has_product_id ^ has_category_id ^ has_new_product):
            raise serializers.ValidationError(
                "You must specify exactly one of: 'product_id', 'category_id', or 'new_product'."
            )

        if has_new_product:
            new_product_data = data["new_product"]
            try:
                brand = Brand.objects.get(name__iexact=new_product_data["brand"])
                category = Category.objects.get(name__iexact=new_product_data["category"])
                data["new_product"]["brand_instance"] = brand
                data["new_product"]["category_instance"] = category
            except Brand.DoesNotExist:
                raise serializers.ValidationError({"new_product": {"brand": "This brand does not exist."}})
            except Category.DoesNotExist:
                raise serializers.ValidationError({"new_product": {"category": "This category does not exist."}})

        return data

    def create(self, validated_data):
        request_user = self.context["request"].user
        store = Store.objects.get(id=validated_data["store_id"])

        target_type = None
        product_target = None
        category_target = None

        if "new_product" in validated_data:
            target_type = Discount.TARGET_PRODUCT
            product_data = validated_data.pop("new_product")
            
            # Check if product brand matches store brand
            if product_data["brand_instance"] != store.brand:
                raise serializers.ValidationError("New product's brand must match the store's brand.")

            product_target = Product.objects.create(
                store=store,
                brand=product_data["brand_instance"],
                category=product_data["category_instance"],
                name=product_data["name"],
                price=product_data["price"],
                price_unit=product_data.get("price_unit", Product.PER_PIECE),
                weight=product_data.get("weight", 0),
                description=product_data.get("description", ""),
            )
        elif "product_id" in validated_data:
            target_type = Discount.TARGET_PRODUCT
            product_target = Product.objects.get(id=validated_data["product_id"])
        elif "category_id" in validated_data:
            target_type = Discount.TARGET_CATEGORY
            category_target = Category.objects.get(id=validated_data["category_id"])

        # Remove fields that are not on the Discount model before creating it
        validated_data.pop("store_id", None)
        validated_data.pop("category_id", None)
        validated_data.pop("product_id", None)

        discount = Discount.objects.create(
            target_type=target_type,
            product=product_target,
            category=category_target,
            **validated_data
        )
        return discount


class BrandSerializer(serializers.ModelSerializer):
    stores_count = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()
    active_discounts_count = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = [
            "id",
            "name",
            "stores_count",
            "products_count",
            "active_discounts_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")

    def get_stores_count(self, obj):
        return obj.stores.count()

    def get_products_count(self, obj):
        return obj.products.count()

    def get_active_discounts_count(self, obj):
        now = timezone.now()
        return Discount.objects.filter(
            product__brand=obj,
            starts_at__lte=now,
            ends_at__gte=now,
            status=Discount.STATUS_APPROVED
        ).count()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class StoreSerializer(serializers.ModelSerializer):
    brand = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all())

    class Meta:
        model = Store
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        instance = Discount(**attrs)
        instance.clean()
        return attrs


class ProductSerializer(serializers.ModelSerializer):
    discounts = DiscountSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        brand = attrs.get("brand") or getattr(self.instance, "brand", None)
        store = attrs.get("store") or getattr(self.instance, "store", None)
        if brand and store and brand != store.brand:
            raise serializers.ValidationError("Product brand must match the brand of the store.")
        return attrs


class ProductDiscountHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDiscountHistory
        fields = "__all__"
        read_only_fields = ("id", "applied_at")
