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
)

app_name = "catalog"

router = DefaultRouter()
router.register(r"brands", BrandViewSet)
router.register(r"categories", CategoryViewSet)
router.register(r"stores", StoreViewSet)
router.register(r"products", ProductViewSet)
router.register(r"discounts", DiscountViewSet)
router.register(r"product-discount-history", ProductDiscountHistoryViewSet, basename="product-discount-history")

urlpatterns = [
    # ... your other url patterns
    path("user/discounts/", UserDiscountListCreateView.as_view(), name="user-discount-list-create"),
]

urlpatterns += router.urls
