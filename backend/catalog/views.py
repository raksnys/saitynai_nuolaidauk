from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from fuzzywuzzy import process
from rest_framework.decorators import action

from .models import (
    Brand,
    Category,
    Discount,
    Product,
    ProductDiscountHistory,
    Store,
    WishlistItem,
    Report,
    ShoppingCart,
    ShoppingCartItem,
)
from .pagination import StandardResultsSetPagination
from .filters import ProductFilter
from .serializers import (
    BrandSerializer,
    CategorySerializer,
    DiscountSerializer,
    DiscountModerationSerializer,
    ProductDiscountHistorySerializer,
    ProductSerializer,
    StoreSerializer,
    UserDiscountCreateSerializer,
    UserDiscountListSerializer,
    WishlistItemSerializer,
    ReportCreateSerializer,
    ReportModerationSerializer,
    ShoppingCartSerializer,
    ShoppingCartItemSerializer,
)
from users.helpers.permissions import IsModeratorOrAdmin


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

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [permissions.AllowAny]
        else:
            self.permission_classes = [IsModeratorOrAdmin]
        return super().get_permissions()


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

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [permissions.AllowAny]
        else:
            self.permission_classes = [IsModeratorOrAdmin]
        return super().get_permissions()


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

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [permissions.AllowAny]
        else:
            self.permission_classes = [IsModeratorOrAdmin]
        return super().get_permissions()


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
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ProductFilter
    ordering_fields = ["name", "price"]

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        query = request.query_params.get('q', None)
        if not query:
            return Response({"error": "Query parameter 'q' is required."}, status=status.HTTP_400_BAD_REQUEST)

        products = Product.objects.all()
        product_names = [p.name for p in products]
        
        # Use fuzzywuzzy to find matches
        matches = process.extract(query, product_names, limit=10)
        
        # Get the product IDs of the best matches
        matched_product_names = [match[0] for match in matches if match[1] > 75] # score threshold
        
        # Retrieve the full product objects
        matched_products = Product.objects.filter(name__in=matched_product_names)
        
        serializer = self.get_serializer(matched_products, many=True)
        return Response(serializer.data)

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'search']:
            self.permission_classes = [permissions.AllowAny]
        else:
            self.permission_classes = [IsModeratorOrAdmin]
        return super().get_permissions()


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
    get=extend_schema(tags=["Wishlist"], summary="List wishlist items"),
    post=extend_schema(tags=["Wishlist"], summary="Add product to wishlist"),
)
class WishlistListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WishlistItemSerializer

    def get_queryset(self):
        return (
            WishlistItem.objects
            .filter(user=self.request.user)
            .select_related("product")
            .prefetch_related("product__discount_history__discount")
        )

    def perform_create(self, serializer):
        product = serializer.validated_data.get("product")
        # Enforce: user can wishlist a product only once
        WishlistItem.objects.get_or_create(user=self.request.user, product=product)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # get_or_create ensures uniqueness
        obj, created = WishlistItem.objects.get_or_create(
            user=request.user, product=serializer.validated_data["product"]
        )
        out = WishlistItemSerializer(obj)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        headers = self.get_success_headers(out.data)
        return Response(out.data, status=status_code, headers=headers)


@extend_schema_view(
    delete=extend_schema(tags=["Wishlist"], summary="Remove product from wishlist"),
)
class WishlistDestroyView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WishlistItemSerializer
    lookup_url_kwarg = "product_id"

    def get_object(self):
        # Allow deletion by product id, not wishlist item id
        product_id = self.kwargs.get(self.lookup_url_kwarg)
        return generics.get_object_or_404(WishlistItem, user=self.request.user, product_id=product_id)


@extend_schema_view(
    post=extend_schema(tags=["Reports"], summary="Report a product or a discount"),
)
class ReportCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReportCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        out = ReportModerationSerializer(obj)
        headers = self.get_success_headers(out.data)
        return Response(out.data, status=status.HTTP_201_CREATED, headers=headers)


@extend_schema_view(
    get=extend_schema(tags=["Reports"], summary="List reported items (moderation)")
)
class ReportModerationListView(generics.ListAPIView):
    permission_classes = [IsModeratorOrAdmin]
    serializer_class = ReportModerationSerializer

    def get_queryset(self):
        qs = Report.objects.select_related("product", "discount", "reported_by").all().order_by("-created_at")
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)
        return qs


@extend_schema_view(
    get=extend_schema(tags=["Reports"], summary="Retrieve a report (moderation)"),
    patch=extend_schema(tags=["Reports"], summary="Update report status (moderation)"),
)
class ReportModerationDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsModeratorOrAdmin]
    serializer_class = ReportModerationSerializer
    queryset = Report.objects.select_related("product", "discount", "reported_by").all()


@extend_schema_view(
    get=extend_schema(tags=["Discounts Moderation"], summary="List submitted discounts (moderation)"),
)
class DiscountModerationListView(generics.ListAPIView):
    permission_classes = [IsModeratorOrAdmin]
    serializer_class = DiscountModerationSerializer

    def get_queryset(self):
        qs = Discount.objects.select_related("brand", "category", "product", "store", "submitted_by").order_by("-created_at")
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)
        return qs


@extend_schema_view(
    get=extend_schema(tags=["Discounts Moderation"], summary="Retrieve a discount (moderation)"),
    patch=extend_schema(tags=["Discounts Moderation"], summary="Update discount status (moderation)"),
)
class DiscountModerationDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsModeratorOrAdmin]
    serializer_class = DiscountModerationSerializer
    queryset = Discount.objects.select_related("brand", "category", "product", "store", "submitted_by").all()


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
        """Inject the current user. Supports store-wide, category-in-store, and product discounts."""
        serializer.save(submitted_by=self.request.user)


@extend_schema_view(
    list=extend_schema(tags=["Shopping Carts"], summary="List your shopping carts"),
    retrieve=extend_schema(tags=["Shopping Carts"], summary="Get a shopping cart"),
    create=extend_schema(tags=["Shopping Carts"], summary="Create a shopping cart"),
)
class ShoppingCartViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ShoppingCartSerializer

    def get_queryset(self):
        qs = (
            ShoppingCart.objects
            .filter(user=self.request.user)
            .prefetch_related("items__product__brand")
        )
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param.upper())
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        tags=["Shopping Carts"],
        summary="Add or increase an item",
        request=ShoppingCartItemSerializer,
        responses={200: ShoppingCartSerializer},
    )
    @action(detail=True, methods=["post"], url_path="add-item")
    def add_item(self, request, pk=None):
        cart: ShoppingCart = self.get_object()
        product_id = request.data.get("product")
        quantity = int(request.data.get("quantity", 1))
        if not product_id:
            return Response({"detail": "'product' is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            product = Product.objects.select_related("brand").get(pk=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        item, _ = ShoppingCartItem.objects.get_or_create(shopping_cart=cart, product=product)
        if quantity < 1:
            quantity = 1
        item.quantity = item.quantity + quantity - 1 if request.data.get("increment", False) else quantity
        item.save()
        out = ShoppingCartSerializer(cart)
        return Response(out.data)

    @extend_schema(
        tags=["Shopping Carts"],
        summary="Update item quantity/purchased",
        request=ShoppingCartItemSerializer,
        responses={200: ShoppingCartSerializer},
    )
    @action(detail=True, methods=["patch"], url_path="update-item")
    def update_item(self, request, pk=None):
        cart: ShoppingCart = self.get_object()
        product_id = request.data.get("product")
        if not product_id:
            return Response({"detail": "'product' is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            item = ShoppingCartItem.objects.select_related("product").get(shopping_cart=cart, product_id=product_id)
        except ShoppingCartItem.DoesNotExist:
            return Response({"detail": "Item not found in this cart."}, status=status.HTTP_404_NOT_FOUND)

        if "quantity" in request.data:
            try:
                q = int(request.data.get("quantity", 1))
            except ValueError:
                return Response({"detail": "'quantity' must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
            item.quantity = max(q, 1)
        if "is_purchased" in request.data:
            item.is_purchased = bool(request.data.get("is_purchased"))
        item.save()
        out = ShoppingCartSerializer(cart)
        return Response(out.data)

    @extend_schema(
        tags=["Shopping Carts"],
        summary="Remove an item",
        request=ShoppingCartItemSerializer,
        responses={200: ShoppingCartSerializer},
    )
    @action(detail=True, methods=["delete"], url_path="remove-item")
    def remove_item(self, request, pk=None):
        cart: ShoppingCart = self.get_object()
        product_id = request.data.get("product") or request.query_params.get("product")
        if not product_id:
            return Response({"detail": "'product' is required."}, status=status.HTTP_400_BAD_REQUEST)
        ShoppingCartItem.objects.filter(shopping_cart=cart, product_id=product_id).delete()
        out = ShoppingCartSerializer(cart)
        return Response(out.data)

    @extend_schema(
        tags=["Shopping Carts"],
        summary="Close the cart",
        responses={200: ShoppingCartSerializer},
    )
    @action(detail=True, methods=["post"], url_path="close")
    def close(self, request, pk=None):
        cart: ShoppingCart = self.get_object()
        cart.status = ShoppingCart.Status.CLOSED
        cart.save(update_fields=["status", "updated_at"])
        out = ShoppingCartSerializer(cart)
        return Response(out.data)
