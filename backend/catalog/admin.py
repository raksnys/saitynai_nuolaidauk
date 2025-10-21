from django.contrib import admin
from .models import (
    Brand,
    Category,
    Store,
    Discount,
    Product,
    ProductDiscountHistory,
    WishlistItem,
    Report,
)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("__str__", "city", "country", "created_at")
    list_filter = ("brand", "city", "country")
    search_fields = ("brand__name", "nickname", "city", "address_line1")


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "discount_type",
        "value",
        "target_type",
        "starts_at",
        "ends_at",
        "status",
        "effective_status",
        "submitted_by",
    )
    list_filter = ("status", "discount_type", "target_type")
    search_fields = ("name", "description")
    autocomplete_fields = ("brand", "category", "product", "submitted_by")

    @admin.display(description="Effective Status")
    def effective_status(self, obj):
        return obj.effective_status


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "store", "brand", "category", "price", "price_unit")
    list_filter = ("store__brand", "category", "price_unit")
    search_fields = ("name", "description", "store__name")
    autocomplete_fields = ("store", "brand", "category")


@admin.register(ProductDiscountHistory)
class ProductDiscountHistoryAdmin(admin.ModelAdmin):
    list_display = ("product", "discount", "applied_at", "removed_at", "applied_price")
    list_filter = ("discount",)
    autocomplete_fields = ("product", "discount")


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    search_fields = ("user__email", "product__name")
    autocomplete_fields = ("user", "product")


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "discount",
        "product_reason",
        "status",
        "reported_by",
        "created_at",
    )
    list_filter = ("status", "product_reason")
    search_fields = ("description", "product__name")
    autocomplete_fields = ("product", "discount", "reported_by")
