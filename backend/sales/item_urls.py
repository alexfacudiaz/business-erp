from rest_framework.routers import DefaultRouter

from .views import SaleItemViewSet

router = DefaultRouter()

router.register(
    r'',
    SaleItemViewSet,
    basename='sale-item',
)

urlpatterns = router.urls