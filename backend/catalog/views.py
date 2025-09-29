from rest_framework import viewsets

from .models import Brand, Category, Discount, Product, ProductDiscountHistory, Store
from .serializers import (
    BrandSerializer,
    CategorySerializer,
    DiscountSerializer,
    ProductDiscountHistorySerializer,
    ProductSerializer,
    StoreSerializer,
)


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all().order_by("name")
    serializer_class = BrandSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.select_related("brand").all()
    serializer_class = StoreSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = (
        Product.objects.select_related("brand", "category", "store")
        .prefetch_related("discounts")
        .all()
    )
    serializer_class = ProductSerializer


class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.select_related("brand", "category", "product").all()
    serializer_class = DiscountSerializer


class ProductDiscountHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductDiscountHistory.objects.select_related("product", "discount").all()
    serializer_class = ProductDiscountHistorySerializer
