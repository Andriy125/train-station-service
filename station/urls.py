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
router.register('station', StationViewSet)
router.register('route', RouteViewSet)
router.register('train', TrainViewSet)
router.register('train-types', TrainTypeViewSet)
router.register('crew', CrewViewSet)
router.register('journeys', JourneyViewSet)
router.register('order', OrderViewSet)
router.register('Ticket', TicketViewSet)

urlpatterns = router.urls