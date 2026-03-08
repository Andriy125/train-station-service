from rest_framework import viewsets
from station.models import (
    Station,
    Route,
    TrainType,
    Train,
    Crew,
    Journey,
    Order,
    Ticket
)
from station.serializers import (
    StationSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    RouteCreateSerializer,
    TrainTypeSerializer,
    TrainListSerializer,
    TrainDetailSerializer,
    TrainCreateSerializer,
    CrewSerializer,
    JourneyListSerializer,
    JourneyDetailSerializer,
    JourneyCreateSerializer,
    OrderSerializer,
    TicketSerializer,
)


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related('source', 'destination')

    def get_serializer_class(self):
        if self.action == 'list':
            return RouteListSerializer
        elif self.action == 'retrieve':
            return RouteDetailSerializer
        return RouteCreateSerializer



class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.select_related('train_type')

    def get_serializer_class(self):
        if self.action == 'list':
            return TrainListSerializer
        elif self.action == 'retrieve':
            return TrainDetailSerializer
        return TrainCreateSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = (Journey.objects
    .select_related(
        'route',
        'train',
    ).prefetch_related(
        'crew'
    ))

    def get_serializer_class(self):
        if self.action == 'list':
            return JourneyListSerializer
        elif self.action == 'retrieve':
            return JourneyDetailSerializer
        return JourneyCreateSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

