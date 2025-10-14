from rest_framework import generics, permissions, viewsets
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse

from .models import Brand, Category, Discount, Product, ProductDiscountHistory, Store
from .serializers import (
    BrandSerializer,
    CategorySerializer,
    DiscountSerializer,
    ProductDiscountHistorySerializer,
    ProductSerializer,
    StoreSerializer,
    UserDiscountCreateSerializer,
    UserDiscountListSerializer,
)


@extend_schema_view(
    list=extend_schema(tags=["Brands"], summary="List brands"),
    retrieve=extend_schema(tags=["Brands"], summary="Get brand"),
    create=extend_schema(tags=["Brands"], summary="Create brand"),
    update=extend_schema(tags=["Brands"], summary="Update brand"),
    partial_update=extend_schema(tags=["Brands"], summary="Partially update brand"),
    destroy=extend_schema(tags=["Brands"], summary="Delete brand"),
)
class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all().order_by("name")
    serializer_class = BrandSerializer


@extend_schema_view(
    list=extend_schema(tags=["Categories"], summary="List categories"),
    retrieve=extend_schema(tags=["Categories"], summary="Get category"),
    create=extend_schema(tags=["Categories"], summary="Create category"),
    update=extend_schema(tags=["Categories"], summary="Update category"),
    partial_update=extend_schema(tags=["Categories"], summary="Partially update category"),
    destroy=extend_schema(tags=["Categories"], summary="Delete category"),
)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer


@extend_schema_view(
    list=extend_schema(tags=["Stores"], summary="List stores"),
    retrieve=extend_schema(tags=["Stores"], summary="Get store"),
    create=extend_schema(tags=["Stores"], summary="Create store"),
    update=extend_schema(tags=["Stores"], summary="Update store"),
    partial_update=extend_schema(tags=["Stores"], summary="Partially update store"),
    destroy=extend_schema(tags=["Stores"], summary="Delete store"),
)
class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.select_related("brand").all()
    serializer_class = StoreSerializer


@extend_schema_view(
    list=extend_schema(tags=["Products"], summary="List products"),
    retrieve=extend_schema(tags=["Products"], summary="Get product"),
    create=extend_schema(tags=["Products"], summary="Create product"),
    update=extend_schema(tags=["Products"], summary="Update product"),
    partial_update=extend_schema(tags=["Products"], summary="Partially update product"),
    destroy=extend_schema(tags=["Products"], summary="Delete product"),
)
class ProductViewSet(viewsets.ModelViewSet):
    queryset = (
        Product.objects.select_related("brand", "category", "store")
        .prefetch_related("discounts")
        .all()
    )
    serializer_class = ProductSerializer


@extend_schema_view(
    list=extend_schema(tags=["Discounts"], summary="List discounts"),
    retrieve=extend_schema(tags=["Discounts"], summary="Get discount"),
    create=extend_schema(tags=["Discounts"], summary="Create discount"),
    update=extend_schema(tags=["Discounts"], summary="Update discount"),
    partial_update=extend_schema(tags=["Discounts"], summary="Partially update discount"),
    destroy=extend_schema(tags=["Discounts"], summary="Delete discount"),
)
class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.select_related("brand", "category", "product").all()
    serializer_class = DiscountSerializer


@extend_schema_view(
    list=extend_schema(tags=["Product Discount History"], summary="List product discount history"),
    retrieve=extend_schema(tags=["Product Discount History"], summary="Get product discount history"),
)
class ProductDiscountHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductDiscountHistory.objects.select_related("product", "discount").all()
    serializer_class = ProductDiscountHistorySerializer


@extend_schema_view(
    get=extend_schema(
        tags=["User Discounts"],
        summary="List submitted discounts",
        description="Returns discounts submitted by the current user in reverse chronological order.",
        responses={200: OpenApiResponse(UserDiscountListSerializer(many=True))},
        request=None,
    ),
    post=extend_schema(
        tags=["User Discounts"],
        summary="Submit a new discount",
        description=(
            "Submit a discount targeting a product or category. Exactly one of product_id, "
            "category_id, or new_product must be provided. When providing new_product, its brand "
            "must match the store's brand."
        ),
        request=UserDiscountCreateSerializer,
        responses={201: OpenApiResponse(UserDiscountListSerializer)},
    ),
)
class UserDiscountListCreateView(generics.ListCreateAPIView):
    """
    - POST: Allows authenticated users to submit a new discount for a product or category.
    - GET: Allows authenticated users to see a history of their submitted discounts.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserDiscountCreateSerializer
        return UserDiscountListSerializer

    def get_queryset(self):
        """This view should only return discounts submitted by the current user."""
        return Discount.objects.filter(submitted_by=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        """Inject the current user into the submitted_by field."""
        serializer.save(submitted_by=self.request.user)
