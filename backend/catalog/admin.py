from django.contrib import admin

from . import models


@admin.register(models.Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)


class ProductDiscountHistoryInline(admin.TabularInline):
    model = models.ProductDiscountHistory
    readonly_fields = ("applied_at", "removed_at", "applied_price")
    extra = 0


@admin.register(models.Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("brand", "nickname", "city", "state", "country", "created_at")
    list_filter = ("brand", "city", "country")
    search_fields = ("brand__name", "nickname", "city")


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "store", "category", "price", "price_unit", "weight")
    list_filter = ("brand", "store", "category", "price_unit")
    search_fields = ("name", "brand__name", "store__nickname")
    inlines = [ProductDiscountHistoryInline]


@admin.register(models.Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "discount_type",
        "value",
        "target_type",
        "brand",
        "category",
        "product",
        "is_active",
    )
    list_filter = ("discount_type", "target_type", "is_active")
    search_fields = ("name", "brand__name", "category__name", "product__name")


@admin.register(models.ProductDiscountHistory)
class ProductDiscountHistoryAdmin(admin.ModelAdmin):
    list_display = ("product", "discount", "applied_price", "applied_at", "removed_at")
    list_filter = ("discount__discount_type",)
    search_fields = ("product__name", "discount__name")
    raw_id_fields = ("product", "discount")
