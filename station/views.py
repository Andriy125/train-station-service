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
from django.db.models import Count, F, ExpressionWrapper, IntegerField
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

    JourneyListSerializer,
    JourneyDetailSerializer,
    JourneyCreateSerializer,

    OrderSerializer,
    OrderListSerializer,
    OrderDetailSerializer,

    TicketListSerializer,
    TicketDetailSerializer, OrderCreateSerializer,
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

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        return {
            'list': StationListSerializer,
            'retrieve': StationDetailSerializer,
        }.get(self.action, StationCreateSerializer)


@extend_schema_view(**route_docs)
class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related('source', 'destination')
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        return {
            'list': RouteListSerializer,
            'retrieve': RouteDetailSerializer,
        }.get(self.action, RouteCreateSerializer)


@extend_schema_view(**train_type_docs)
class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    permission_classes = [IsAdminUser]


@extend_schema_view(**train_docs)
class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.select_related('train_type')

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        return {
            'list': TrainListSerializer,
            'retrieve': TrainDetailSerializer,
        }.get(self.action, TrainCreateSerializer)


@extend_schema_view(**crew_docs)
class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        return {
            'list': CrewListSerializer,
        }.get(self.action, CrewDetailSerializer)


@extend_schema_view(**journey_docs)
class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.none()
    filterset_class = JourneyFilter

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        return (
            Journey.objects
            .select_related("route", "train")
            .prefetch_related("crew")
            .annotate(available_seats=self._calc_available_seats())
        )

    @staticmethod
    def _calc_available_seats():
        return ExpressionWrapper(
            F("train__cargo_num") * F("train__places_in_cargo") - Count("tickets"),
            output_field=IntegerField()
        )

    def get_serializer_class(self):
        return {
            'list': JourneyListSerializer,
            'retrieve': JourneyDetailSerializer,
        }.get(self.action, JourneyCreateSerializer)


@extend_schema_view(**order_docs)
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.none()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return self._get_all_orders()
        return self._get_user_orders(user)

    @staticmethod
    def _get_all_orders():
        return Order.objects.all().prefetch_related('tickets')

    @staticmethod
    def _get_user_orders(user):
        return Order.objects.filter(user=user).prefetch_related('tickets')

    def get_serializer_class(self):
        return {
            'list': OrderListSerializer,
            'retrieve': OrderDetailSerializer,
            'create': OrderCreateSerializer,
        }.get(self.action, OrderSerializer)


@extend_schema_view(**ticket_docs)
class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ticket.objects.none()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Ticket.objects.filter(
            order__user=self.request.user
        ).select_related('journey', 'order')

    def get_serializer_class(self):
        return {
            'list': TicketListSerializer,
        }.get(self.action, TicketDetailSerializer)
