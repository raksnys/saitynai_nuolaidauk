from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    BrandViewSet,
    CategoryViewSet,
    DiscountViewSet,
    ProductDiscountHistoryViewSet,
    ProductViewSet,
    StoreViewSet,
    UserDiscountListCreateView,
    WishlistListCreateView,
    WishlistDestroyView,
    ReportCreateView,
    ReportModerationListView,
    ReportModerationDetailView,
    DiscountModerationListView,
    DiscountModerationDetailView,
    ShoppingCartViewSet,
)

app_name = "catalog"

router = DefaultRouter()
router.register(r"brands", BrandViewSet)
router.register(r"categories", CategoryViewSet)
router.register(r"stores", StoreViewSet)
router.register(r"products", ProductViewSet)
router.register(r"discounts", DiscountViewSet)
router.register(r"product-discount-history", ProductDiscountHistoryViewSet, basename="product-discount-history")
router.register(r"shopping-carts", ShoppingCartViewSet, basename="shopping-carts")

urlpatterns = [
    # ... your other url patterns
    path("user/discounts/", UserDiscountListCreateView.as_view(), name="user-discount-list-create"),
    path("user/wishlist/", WishlistListCreateView.as_view(), name="wishlist-list-create"),
    path("user/wishlist/<int:product_id>/", WishlistDestroyView.as_view(), name="wishlist-destroy"),
    # Reports
    path('reports/', ReportCreateView.as_view(), name='report-create'),  # POST by authenticated users
    path('reports/moderation/', ReportModerationListView.as_view(), name='report-list'),  # GET by moderators/admins
    path('reports/moderation/<int:pk>/', ReportModerationDetailView.as_view(), name='report-detail'),  # GET/PATCH by moderators/admins
    # Discounts moderation
    path('discounts/moderation/', DiscountModerationListView.as_view(), name='discount-list'),
    path('discounts/moderation/<int:pk>/', DiscountModerationDetailView.as_view(), name='discount-detail'),
]

urlpatterns += router.urls
