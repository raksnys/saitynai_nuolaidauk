from rest_framework import serializers

from .models import (
    Brand,
    Category,
    Discount,
    Product,
    ProductDiscountHistory,
    Store,
)


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


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
