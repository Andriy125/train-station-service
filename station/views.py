from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

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


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'list':
            return StationListSerializer
        elif self.action == 'retrieve':
            return StationDetailSerializer
        return StationCreateSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related('source', 'destination')
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'list':
            return RouteListSerializer
        elif self.action == 'retrieve':
            return RouteDetailSerializer
        return RouteCreateSerializer


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    permission_classes = [IsAdminUser]


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
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'list':
            return CrewListSerializer
        elif self.action == 'retrieve':
            return CrewDetailSerializer
        return CrewCreateSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = (Journey.objects
    .select_related(
        'route',
        'train',
    ).prefetch_related(
        'crew'
    ))

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
