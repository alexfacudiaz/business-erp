from rest_framework.routers import DefaultRouter

from .views import PurchaseItemViewSet

router = DefaultRouter()

router.register(
    r'',
    PurchaseItemViewSet,
    basename='purchase-item',
)

urlpatterns = router.urls