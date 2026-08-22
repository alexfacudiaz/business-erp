from rest_framework.routers import DefaultRouter

from .views import StockAdjustmentItemViewSet


router = DefaultRouter()
router.register(
    r'',
    StockAdjustmentItemViewSet,
    basename='stock-adjustment-item',
)

urlpatterns = router.urls