from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DebtViewSet, DrinkingViewSet, ParticipationViewSet, DrinksViewSet, LocationsViewSet

router = DefaultRouter()
router.register(r'debts', DebtViewSet)
router.register(r'drinkings', DrinkingViewSet)
router.register(r'participations', ParticipationViewSet)
router.register(r'drinks', DrinksViewSet)
router.register(r'locations', LocationsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]