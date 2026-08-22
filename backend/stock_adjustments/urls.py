from rest_framework.routers import DefaultRouter

from .views import StockAdjustmentViewSet


router = DefaultRouter()
router.register(
    r'',
    StockAdjustmentViewSet,
    basename='stock-adjustment',
)

urlpatterns = router.urls