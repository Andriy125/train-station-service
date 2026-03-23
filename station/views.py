from rest_framework import viewsets
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    AllowAny
)
from station.filters import JourneyFilter
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
    StationListSerializer,
    StationDetailSerializer,
    StationCreateSerializer,

    RouteListSerializer,
    RouteDetailSerializer,
    RouteCreateSerializer,

    TrainTypeSerializer,

    TrainListSerializer,
    TrainDetailSerializer,
    TrainCreateSerializer,

    CrewListSerializer,
    CrewDetailSerializer,
    CrewCreateSerializer,

    JourneyListSerializer,
    JourneyDetailSerializer,
    JourneyCreateSerializer,

    OrderSerializer,
    OrderListSerializer,
    OrderDetailSerializer,

    TicketSerializer,
    TicketListSerializer,
    TicketDetailSerializer,
)
from drf_spectacular.utils import extend_schema_view
from .swagger_docs import (
    station_docs,
    route_docs,
    train_type_docs,
    train_docs,
    crew_docs,
    journey_docs,
    order_docs,
    ticket_docs,
)


@extend_schema_view(**station_docs)
class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'list':
            return StationListSerializer
        elif self.action == 'retrieve':
            return StationDetailSerializer
        return StationCreateSerializer


@extend_schema_view(**route_docs)
class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related('source', 'destination')
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'list':
            return RouteListSerializer
        elif self.action == 'retrieve':
            return RouteDetailSerializer
        return RouteCreateSerializer


@extend_schema_view(**train_type_docs)
class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    permission_classes = [IsAdminUser]


@extend_schema_view(**train_docs)
class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.select_related('train_type')

    def get_serializer_class(self):
        if self.action == 'list':
            return TrainListSerializer
        elif self.action == 'retrieve':
            return TrainDetailSerializer
        return TrainCreateSerializer


@extend_schema_view(**crew_docs)
class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'list':
            return CrewListSerializer
        elif self.action == 'retrieve':
            return CrewDetailSerializer
        return CrewCreateSerializer


@extend_schema_view(**journey_docs)
class JourneyViewSet(viewsets.ModelViewSet):
    queryset = (Journey.objects
    .select_related(
        'route',
        'train',
    ).prefetch_related(
        'crew'
    ))

    filterset_class = JourneyFilter

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.action == 'list':
            return JourneyListSerializer
        elif self.action == 'retrieve':
            return JourneyDetailSerializer
        return JourneyCreateSerializer


@extend_schema_view(**order_docs)
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.none()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Order.objects.all().prefetch_related('tickets')

        return Order.objects.filter(
            user=user
        ).prefetch_related('tickets')

    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        elif self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderSerializer


@extend_schema_view(**ticket_docs)
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.none()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Ticket.objects.filter(order__user=self.request.user)
        if self.action in ['list', 'retrieve']:
            queryset = queryset.select_related('journey', 'order')
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return TicketListSerializer
        elif self.action == 'retrieve':
            return TicketDetailSerializer
        return TicketSerializer
