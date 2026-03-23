from rest_framework.routers import DefaultRouter
from station.views import (
    StationViewSet,
    RouteViewSet,
    TrainTypeViewSet,
    TrainViewSet,
    CrewViewSet,
    JourneyViewSet,
    OrderViewSet,
    TicketViewSet,
)

router = DefaultRouter()
router.register('stations', StationViewSet)
router.register('routes', RouteViewSet)
router.register('trains', TrainViewSet)
router.register('train-types', TrainTypeViewSet)
router.register('crews', CrewViewSet)
router.register('journeys', JourneyViewSet)
router.register('orders', OrderViewSet)
router.register('tickets', TicketViewSet)

urlpatterns = router.urls