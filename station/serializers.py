from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers

from station.models import (
    Station,
    Route,
    TrainType,
    Train,
    Crew,
    Journey,
    Order,
    Ticket,
)

class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = '__all__'


class StationListSerializer(StationSerializer):
    class Meta(StationSerializer.Meta):
        fields = (
            'id',
            'name',
        )


class StationDetailSerializer(StationSerializer):
    pass


class StationCreateSerializer(StationSerializer):
    pass


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = '__all__'


class RouteListSerializer(RouteSerializer):
    source = serializers.StringRelatedField()
    destination = serializers.StringRelatedField()

    class Meta(RouteSerializer.Meta):
        fields = (
            'id',
            'source',
            'destination',
            'distance',
        )


class RouteDetailSerializer(RouteSerializer):
    source = StationSerializer(read_only=True)
    destination = StationSerializer(read_only=True)


class RouteCreateSerializer(RouteSerializer):
    source_id = serializers.PrimaryKeyRelatedField(
        queryset=Station.objects.all(),
        source='source',
    )
    destination_id = serializers.PrimaryKeyRelatedField(
        queryset=Station.objects.all(),
        source='destination',
    )

    class Meta(RouteSerializer.Meta):
        fields = (
            'source_id',
            'destination_id',
            'distance',
        )

    def to_representation(self, instance):
        return RouteListSerializer(instance, context=self.context).data


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = '__all__'


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = '__all__'


class TrainListSerializer(TrainSerializer):
    train_type = serializers.StringRelatedField()

    class Meta(TrainSerializer.Meta):
        fields = (
            'id',
            'name',
            "cargo_num",
            "places_in_cargo",
            "train_type",
        )


class TrainDetailSerializer(TrainSerializer):
    train_type = TrainTypeSerializer(read_only=True)

    class Meta(TrainSerializer.Meta):
        fields = (
            'id',
            'name',
            "train_type",
            "cargo_num",
            "places_in_cargo",
        )


class TrainCreateSerializer(serializers.ModelSerializer):
    train_type_id = serializers.PrimaryKeyRelatedField(
        queryset=TrainType.objects.all(),
        source='train_type',
    )

    class Meta(TrainSerializer.Meta):
        fields = (
            'id',
            'name',
            "cargo_num",
            "places_in_cargo",
            "train_type_id",
        )


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = '__all__'


class CrewListSerializer(CrewSerializer):
    class Meta(CrewSerializer.Meta):
        fields = (
            'id',
            'full_name',
            'role',
        )


class CrewDetailSerializer(CrewSerializer):
    class Meta(CrewSerializer.Meta):
        fields = (
            'id',
            'first_name',
            'last_name',
            'role',
        )


class CrewCreateSerializer(CrewSerializer):
    class Meta(CrewSerializer.Meta):
        fields = (
            'id',
            'first_name',
            'last_name',
            'role',
        )


class JourneySerializer(serializers.ModelSerializer):

    class Meta:
        model = Journey
        fields = '__all__'


class JourneyListSerializer(JourneySerializer):
    route = serializers.StringRelatedField()
    train = serializers.StringRelatedField()
    crew = serializers.StringRelatedField(many=True)
    available_seats = serializers.IntegerField(read_only=True)

    class Meta(JourneySerializer.Meta):
        fields = (
            "id",
            "route",
            "train",
            "crew",
            "available_seats",
            "departure_date",
            "arrival_date",
        )


class JourneyDetailSerializer(JourneySerializer):
    route = RouteSerializer(read_only=True)
    train = TrainSerializer(read_only=True)
    crew = CrewSerializer(many=True, read_only=True)
    available_seats = serializers.IntegerField(read_only=True)


class JourneyCreateSerializer(JourneySerializer):
    route_id = serializers.PrimaryKeyRelatedField(
        queryset=Route.objects.all(),
        source='route',
    )
    train_id = serializers.PrimaryKeyRelatedField(
        queryset=Train.objects.all(),
        source='train',
    )
    crew_ids = serializers.PrimaryKeyRelatedField(
        queryset=Crew.objects.all(),
        many=True,
        source='crew',
    )

    class Meta(JourneySerializer.Meta):
        fields = (
            "id",
            "route_id",
            "train_id",
            "crew_ids",
            "departure_date",
            "arrival_date",
        )


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('user',)


class OrderListSerializer(OrderSerializer):
    class Meta(OrderSerializer.Meta):
        fields = (
            "id",
            "created_at",
        )


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")

        if request and request.user and not request.user.is_staff:
            if "order" in self.fields:
                self.fields["order"].queryset = Order.objects.filter(user=request.user)

    def validate_order(self, value):
        user = self.context["request"].user
        if value.user != user and not user.is_staff:
            raise serializers.ValidationError("You cannot add tickets to someone else's order.")
        return value


class TicketListSerializer(TicketSerializer):
    journey = serializers.StringRelatedField()

    class Meta(TicketSerializer.Meta):
        fields = (
            "id",
            "journey",
            "cargo",
            "seat",
        )


class TicketDetailSerializer(TicketSerializer):
    journey = JourneyListSerializer(read_only=True)
    order = OrderListSerializer(read_only=True)


class TicketCreateSerializer(TicketSerializer):
    class Meta(TicketSerializer.Meta):
        fields = (
            "id",
            "journey",
            "cargo",
            "seat",
        )

    def validate(self, attrs):
        instance = Ticket(**attrs)
        try:
            instance.full_clean(exclude=["order"])
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        return attrs


class OrderDetailSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
    class Meta(OrderSerializer.Meta):
        fields = (
            "id",
            "created_at",
            "tickets",
        )

class OrderCreateSerializer(OrderSerializer):
    tickets = TicketCreateSerializer(many=True, allow_empty=False)

    class Meta(OrderSerializer.Meta):
        fields = (
            "id",
            "created_at",
            "tickets",
        )

    def validate(self, attrs):
        tickets = attrs.get("tickets")
        if tickets:
            self._validate_tickets_uniqueness(tickets)
            self._validate_seats_availability(tickets)
        return attrs

    @staticmethod
    def _validate_tickets_uniqueness(tickets):
        ticket_list = []
        for ticket in tickets:
            ticket_identity = (ticket["journey"], ticket["cargo"], ticket["seat"])
            if ticket_identity in ticket_list:
                raise serializers.ValidationError(
                    "You cannot order the same ticket multiple times in one order."
                )
            ticket_list.append(ticket_identity)

    @staticmethod
    def _validate_seats_availability(tickets):
        for ticket in tickets:
            if Ticket.objects.filter(
                journey=ticket["journey"],
                cargo=ticket["cargo"],
                seat=ticket["seat"]
            ).exists():
                raise serializers.ValidationError(
                    f"Seat {ticket['seat']} in carriage {ticket['cargo']} "
                    f"for journey {ticket['journey']} is already taken"
                )

    def create(self, validated_data):
        tickets_data = validated_data.pop('tickets')
        with transaction.atomic():
            order = Order.objects.create(
                user=self.context["request"].user,
            )
            for ticket in tickets_data:
                Ticket.objects.create(order=order, **ticket)
            return order

    def to_representation(self, instance):
        return OrderDetailSerializer(instance, context=self.context).data
