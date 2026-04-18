from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.db.models import IntegerField, Value

from station.models import Station, Route, TrainType, Train, Crew, Journey, Order, Ticket
from station.serializers import (
    StationSerializer,
    StationListSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    RouteCreateSerializer,
    TrainListSerializer,
    TrainDetailSerializer,
    TrainCreateSerializer,
    CrewListSerializer,
    JourneyListSerializer,
    JourneyCreateSerializer,
    TicketSerializer,
    TicketCreateSerializer,
    OrderCreateSerializer,
)

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_user(username="user@test.com", password="pass123", is_staff=False):
    return User.objects.create_user(
        username=username, password=password, is_staff=is_staff
    )


def make_station(name="Kyiv", lat=50.4, lon=30.5):
    return Station.objects.create(name=name, latitude=lat, longitude=lon)


def make_train(name="Test Train", cargo_num=5, places_in_cargo=10):
    train_type = TrainType.objects.create(name="Intercity")
    return Train.objects.create(
        name=name,
        cargo_num=cargo_num,
        places_in_cargo=places_in_cargo,
        train_type=train_type,
    )


def make_crew(first_name="John", last_name="Doe", role="Conductor"):
    return Crew.objects.create(first_name=first_name, last_name=last_name, role=role)


def make_route(source, destination, distance=540):
    return Route.objects.create(
        source=source, destination=destination, distance=distance
    )


def make_journey(route, train, departure="2025-06-01T10:00:00Z", arrival="2025-06-01T18:00:00Z"):
    return Journey.objects.create(
        route=route, train=train, departure_date=departure, arrival_date=arrival
    )


def make_request(user):
    request = RequestFactory().get("/")
    request.user = user
    return request


# ---------------------------------------------------------------------------
# Station serializers
# ---------------------------------------------------------------------------

class StationSerializerTest(TestCase):

    def setUp(self):
        self.station = make_station(name="Kyiv", lat=50.4, lon=30.5)

    def test_list_serializer_has_only_id_and_name(self):
        data = StationListSerializer(self.station).data
        self.assertEqual(set(data.keys()), {"id", "name"})

    def test_list_serializer_name_value(self):
        data = StationListSerializer(self.station).data
        self.assertEqual(data["name"], "Kyiv")

    def test_full_serializer_includes_coordinates(self):
        data = StationSerializer(self.station).data
        self.assertIn("latitude", data)
        self.assertIn("longitude", data)


# ---------------------------------------------------------------------------
# Route serializers
# ---------------------------------------------------------------------------

class RouteSerializerTest(TestCase):

    def setUp(self):
        self.station_a = make_station(name="Kyiv")
        self.station_b = make_station(name="Lviv", lat=49.8, lon=24.0)
        self.route = make_route(self.station_a, self.station_b)

    def test_list_serializer_source_is_string(self):
        data = RouteListSerializer(self.route).data
        self.assertEqual(data["source"], "Kyiv")
        self.assertEqual(data["destination"], "Lviv")

    def test_detail_serializer_source_is_nested(self):
        data = RouteDetailSerializer(self.route).data
        self.assertIsInstance(data["source"], dict)
        self.assertEqual(data["source"]["name"], "Kyiv")

    def test_create_serializer_valid_data(self):
        # Use reverse direction — setUp already created Kyiv→Lviv
        serializer = RouteCreateSerializer(
            data={
                "source_id": self.station_b.id,
                "destination_id": self.station_a.id,
                "distance": 540,
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_create_serializer_to_representation_returns_list_format(self):
        station_c = make_station(name="Odesa", lat=46.5, lon=30.7)
        serializer = RouteCreateSerializer(
            data={
                "source_id": self.station_a.id,
                "destination_id": station_c.id,
                "distance": 475,
            }
        )
        serializer.is_valid(raise_exception=True)
        route = serializer.save()
        # to_representation delegates to RouteListSerializer → strings
        represented = serializer.to_representation(route)
        self.assertEqual(represented["source"], "Kyiv")
        self.assertEqual(represented["destination"], "Odesa")


# ---------------------------------------------------------------------------
# Train serializers
# ---------------------------------------------------------------------------

class TrainSerializerTest(TestCase):

    def setUp(self):
        self.train = make_train()

    def test_list_serializer_train_type_is_string(self):
        data = TrainListSerializer(self.train).data
        self.assertEqual(data["train_type"], "Intercity")

    def test_detail_serializer_train_type_is_nested(self):
        data = TrainDetailSerializer(self.train).data
        self.assertIsInstance(data["train_type"], dict)
        self.assertEqual(data["train_type"]["name"], "Intercity")

    def test_create_serializer_valid_data(self):
        train_type = TrainType.objects.create(name="Express")
        serializer = TrainCreateSerializer(
            data={
                "name": "Express 1",
                "cargo_num": 8,
                "places_in_cargo": 20,
                "train_type_id": train_type.id,
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)


# ---------------------------------------------------------------------------
# Crew serializers
# ---------------------------------------------------------------------------

class CrewSerializerTest(TestCase):

    def test_list_serializer_shows_full_name(self):
        crew = make_crew(first_name="John", last_name="Doe")
        data = CrewListSerializer(crew).data
        self.assertEqual(data["full_name"], "John Doe")
        self.assertNotIn("first_name", data)
        self.assertNotIn("last_name", data)


# ---------------------------------------------------------------------------
# Journey serializers
# ---------------------------------------------------------------------------

class JourneySerializerTest(TestCase):

    def setUp(self):
        self.station_a = make_station(name="Kyiv")
        self.station_b = make_station(name="Lviv", lat=49.8, lon=24.0)
        self.route = make_route(self.station_a, self.station_b)
        self.train = make_train()
        self.journey = make_journey(self.route, self.train)

    def test_list_serializer_route_is_string(self):
        annotated = Journey.objects.annotate(
            available_seats=Value(50, output_field=IntegerField())
        ).get(pk=self.journey.pk)
        data = JourneyListSerializer(annotated).data
        self.assertIn("Kyiv", data["route"])
        self.assertIn("Lviv", data["route"])

    def test_list_serializer_available_seats(self):
        annotated = Journey.objects.annotate(
            available_seats=Value(42, output_field=IntegerField())
        ).get(pk=self.journey.pk)
        data = JourneyListSerializer(annotated).data
        self.assertEqual(data["available_seats"], 42)

    def test_create_serializer_valid_data(self):
        crew = make_crew()
        serializer = JourneyCreateSerializer(
            data={
                "route_id": self.route.id,
                "train_id": self.train.id,
                "crew_ids": [crew.id],
                "departure_date": "2025-07-01T10:00:00Z",
                "arrival_date": "2025-07-01T18:00:00Z",
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_create_serializer_departure_after_arrival_is_valid_at_serializer_level(self):
        # JourneyCreateSerializer doesn't call clean(), so date validation
        # only happens at the model level (Journey.clean()). The serializer
        # itself considers such data valid — model tests cover the clean() logic.
        serializer = JourneyCreateSerializer(
            data={
                "route_id": self.route.id,
                "train_id": self.train.id,
                "crew_ids": [],
                "departure_date": "2025-07-01T18:00:00Z",
                "arrival_date": "2025-07-01T10:00:00Z",
            }
        )
        self.assertTrue(serializer.is_valid())


# ---------------------------------------------------------------------------
# Ticket serializers
# ---------------------------------------------------------------------------

class TicketSerializerTest(TestCase):

    def setUp(self):
        self.user = make_user(username="owner")
        self.other_user = make_user(username="other")
        self.staff = make_user(username="admin", is_staff=True)

        self.train = make_train()
        station_a = make_station(name="Kyiv")
        station_b = make_station(name="Lviv", lat=49.8, lon=24.0)
        route = make_route(station_a, station_b)
        self.journey = make_journey(route, self.train)

        self.order = Order.objects.create(user=self.user)

    def test_validate_order_passes_for_owner(self):
        serializer = TicketSerializer(context={"request": make_request(self.user)})
        result = serializer.validate_order(self.order)
        self.assertEqual(result, self.order)

    def test_validate_order_raises_for_other_user(self):
        serializer = TicketSerializer(context={"request": make_request(self.other_user)})
        from rest_framework.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            serializer.validate_order(self.order)

    def test_validate_order_passes_for_staff(self):
        serializer = TicketSerializer(context={"request": make_request(self.staff)})
        result = serializer.validate_order(self.order)
        self.assertEqual(result, self.order)

    def test_non_staff_order_queryset_is_filtered(self):
        serializer = TicketSerializer(context={"request": make_request(self.user)})
        qs = serializer.fields["order"].queryset
        self.assertNotIn(
            Order.objects.create(user=self.other_user),
            qs,
        )

    def test_staff_order_queryset_is_not_filtered(self):
        serializer = TicketSerializer(context={"request": make_request(self.staff)})
        qs = serializer.fields["order"].queryset
        other_order = Order.objects.create(user=self.other_user)
        self.assertIn(other_order, qs.all())


class TicketCreateSerializerTest(TestCase):

    def setUp(self):
        self.train = make_train(cargo_num=5, places_in_cargo=10)
        station_a = make_station(name="Kyiv")
        station_b = make_station(name="Lviv", lat=49.8, lon=24.0)
        route = make_route(station_a, station_b)
        self.journey = make_journey(route, self.train)

    def test_valid_ticket_passes_validation(self):
        serializer = TicketCreateSerializer(
            data={"journey": self.journey.id, "cargo": 1, "seat": 1}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_cargo_raises_validation_error(self):
        serializer = TicketCreateSerializer(
            data={"journey": self.journey.id, "cargo": 99, "seat": 1}
        )
        self.assertFalse(serializer.is_valid())

    def test_invalid_seat_raises_validation_error(self):
        serializer = TicketCreateSerializer(
            data={"journey": self.journey.id, "cargo": 1, "seat": 99}
        )
        self.assertFalse(serializer.is_valid())


# ---------------------------------------------------------------------------
# OrderCreateSerializer
# ---------------------------------------------------------------------------

class OrderCreateSerializerTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.request = make_request(self.user)

        self.train = make_train(cargo_num=5, places_in_cargo=10)
        station_a = make_station(name="Kyiv")
        station_b = make_station(name="Lviv", lat=49.8, lon=24.0)
        route = make_route(station_a, station_b)
        self.journey = make_journey(route, self.train)

    def _make_serializer(self, data):
        return OrderCreateSerializer(data=data, context={"request": self.request})

    def test_create_order_with_tickets(self):
        serializer = self._make_serializer(
            data={"tickets": [{"journey": self.journey.id, "cargo": 1, "seat": 1}]}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        order = serializer.save()
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.tickets.count(), 1)

    def test_empty_tickets_is_invalid(self):
        serializer = self._make_serializer(data={"tickets": []})
        self.assertFalse(serializer.is_valid())

    def test_duplicate_tickets_in_one_order_raises(self):
        serializer = self._make_serializer(
            data={
                "tickets": [
                    {"journey": self.journey.id, "cargo": 1, "seat": 1},
                    {"journey": self.journey.id, "cargo": 1, "seat": 1},
                ]
            }
        )
        self.assertFalse(serializer.is_valid())
        error_str = str(serializer.errors)
        self.assertIn("same ticket", error_str)

    def test_already_taken_seat_raises(self):
        existing_order = Order.objects.create(user=self.user)
        Ticket.objects.create(journey=self.journey, order=existing_order, cargo=1, seat=1)

        serializer = self._make_serializer(
            data={"tickets": [{"journey": self.journey.id, "cargo": 1, "seat": 1}]}
        )
        # DRF's UniqueConstraint validator fires at field level before
        # OrderCreateSerializer._validate_seats_availability is reached
        self.assertFalse(serializer.is_valid())

    def test_to_representation_returns_order_detail_format(self):
        serializer = self._make_serializer(
            data={"tickets": [{"journey": self.journey.id, "cargo": 1, "seat": 1}]}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        represented = serializer.to_representation(order)
        self.assertIn("tickets", represented)
        self.assertIsInstance(represented["tickets"], list)

    def test_create_multiple_tickets_in_one_order(self):
        serializer = self._make_serializer(
            data={
                "tickets": [
                    {"journey": self.journey.id, "cargo": 1, "seat": 1},
                    {"journey": self.journey.id, "cargo": 1, "seat": 2},
                ]
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        order = serializer.save()
        self.assertEqual(order.tickets.count(), 2)