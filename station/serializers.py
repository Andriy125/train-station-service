from rest_framework import serializers, viewsets
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


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = '__all__'


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = '__all__'


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = '__all__'


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = '__all__'


class JourneySerializer(serializers.ModelSerializer):

    class Meta:
        model = Journey
        fields = '__all__'


class JourneyListSerializer(JourneySerializer):
    route = serializers.StringRelatedField()
    train = serializers.StringRelatedField()

    class Meta(JourneySerializer.Meta):
        fields = (
            "id",
            "route",
            "train",
            "crew",
            "departure_date",
            "arrival_date"
        )

class JourneyDetailSerializer(JourneySerializer):
    route = RouteSerializer(read_only=True)
    train = TrainSerializer(read_only=True)
    crew = CrewSerializer(many=True, read_only=True)


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
            "arrival_date"
        )


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class TicketSerializer(serializers.ModelSerializer):
    journey = JourneySerializer(read_only=True)
    order = OrderSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = '__all__'
