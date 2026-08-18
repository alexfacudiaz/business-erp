from rest_framework.routers import DefaultRouter

from .views import StockMovementViewSet


router = DefaultRouter()

router.register(
    r'',
    StockMovementViewSet,
    basename='stock-movement'
)

urlpatterns = router.urls