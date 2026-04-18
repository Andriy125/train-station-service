from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
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
from django.contrib.auth import get_user_model

User = get_user_model()


def create_train(cargo_num=5, places_in_cargo=10):
    train_type = TrainType.objects.create(name="Intercity")
    return Train.objects.create(
        name="Test Train",
        cargo_num=cargo_num,
        places_in_cargo=places_in_cargo,
        train_type=train_type,
    )


def create_crew(first_name="John", last_name="Doe", role="Conductor"):
    return Crew.objects.create(
        first_name=first_name,
        last_name=last_name,
        role=role,
    )


def create_journey(train):
    station_a = Station.objects.create(name="Kyiv", latitude=50.4, longitude=30.5)
    station_b = Station.objects.create(name="Lviv", latitude=49.8, longitude=24.0)
    route = Route.objects.create(source=station_a, destination=station_b, distance=540)
    return Journey.objects.create(
        route=route,
        train=train,
        departure_date="2025-06-01T10:00:00Z",
        arrival_date="2025-06-01T18:00:00Z",
    )


def create_order():
    user = User.objects.create_user(username="test@test.com", password="test123")
    return Order.objects.create(user=user)


class TicketCleanTest(TestCase):

    def setUp(self):
        self.train = create_train(cargo_num=5, places_in_cargo=10)
        self.journey = create_journey(self.train)
        self.order = create_order()

    def test_valid_ticket_passes(self):
        ticket = Ticket(journey=self.journey, order=self.order, cargo=1, seat=1)
        ticket.clean()  # не повинно кидати

    def test_cargo_below_1_raises(self):
        ticket = Ticket(journey=self.journey, order=self.order, cargo=0, seat=1)
        with self.assertRaises(ValidationError):
            ticket.clean()

    def test_seat_below_1_raises(self):
        ticket = Ticket(journey=self.journey, order=self.order, cargo=1, seat=0)
        with self.assertRaises(ValidationError):
            ticket.clean()

    def test_cargo_exceeds_train_wagons_raises(self):
        ticket = Ticket(journey=self.journey, order=self.order, cargo=6, seat=1)
        with self.assertRaises(ValidationError):
            ticket.clean()

    def test_seat_exceeds_places_in_cargo_raises(self):
        ticket = Ticket(journey=self.journey, order=self.order, cargo=1, seat=11)
        with self.assertRaises(ValidationError):
            ticket.clean()

    def test_cargo_at_max_boundary_passes(self):
        ticket = Ticket(journey=self.journey, order=self.order, cargo=5, seat=1)
        ticket.clean()

    def test_seat_at_max_boundary_passes(self):
        ticket = Ticket(journey=self.journey, order=self.order, cargo=1, seat=10)
        ticket.clean()

    def test_save_invalid_ticket_raises(self):
        ticket = Ticket(journey=self.journey, order=self.order, cargo=0, seat=1)
        with self.assertRaises(ValidationError):
            ticket.save()

    def test_duplicate_ticket_raises(self):
        Ticket.objects.create(journey=self.journey, order=self.order, cargo=1, seat=1)
        with self.assertRaises(ValidationError):
            Ticket.objects.create(journey=self.journey, order=self.order, cargo=1, seat=1)


class RouteCleanTest(TestCase):

    def setUp(self):
        self.station_a = Station.objects.create(name="Kyiv", latitude=50.4, longitude=30.5)
        self.station_b = Station.objects.create(name="Lviv", latitude=49.8, longitude=24.0)

    def test_valid_route_passes(self):
        route = Route(source=self.station_a, destination=self.station_b, distance=540)
        route.clean()

    def test_same_source_and_destination_raises(self):
        route = Route(source=self.station_a, destination=self.station_a, distance=0)
        with self.assertRaises(ValidationError):
            route.clean()

    def test_unique_route_constraint(self):
        Route.objects.create(source=self.station_a, destination=self.station_b, distance=540)
        with self.assertRaises(IntegrityError):
            Route.objects.create(source=self.station_a, destination=self.station_b, distance=100)


class JourneyCleanTest(TestCase):

    def setUp(self):
        self.train = create_train()
        station_a = Station.objects.create(name="Kyiv", latitude=50.4, longitude=30.5)
        station_b = Station.objects.create(name="Lviv", latitude=49.8, longitude=24.0)
        self.route = Route.objects.create(source=station_a, destination=station_b, distance=540)

    def test_valid_dates_passes(self):
        journey = Journey(
            route=self.route,
            train=self.train,
            departure_date="2025-06-01T10:00:00Z",
            arrival_date="2025-06-01T18:00:00Z",
        )
        journey.clean()

    def test_departure_after_arrival_raises(self):
        journey = Journey(
            route=self.route,
            train=self.train,
            departure_date="2025-06-01T18:00:00Z",
            arrival_date="2025-06-01T10:00:00Z",
        )
        with self.assertRaises(ValidationError):
            journey.clean()

    def test_departure_equals_arrival_passes(self):
        journey = Journey(
            route=self.route,
            train=self.train,
            departure_date="2025-06-01T10:00:00Z",
            arrival_date="2025-06-01T10:00:00Z",
        )
        journey.clean()


class CrewTest(TestCase):

    def test_full_name_property(self):
        crew = create_crew(first_name="John", last_name="Doe", role="Conductor")
        self.assertEqual(crew.full_name, "John Doe")

    def test_str_representation(self):
        crew = create_crew(first_name="John", last_name="Doe", role="Conductor")
        self.assertEqual(str(crew), "John Doe (Conductor)")


class StrRepresentationTest(TestCase):

    def test_station_str(self):
        station = Station.objects.create(name="Kyiv", latitude=50.4, longitude=30.5)
        self.assertEqual(str(station), "Kyiv")

    def test_train_type_str(self):
        train_type = TrainType.objects.create(name="Intercity")
        self.assertEqual(str(train_type), "Intercity")

    def test_train_str(self):
        train = create_train()
        self.assertEqual(str(train), "Test Train")

    def test_route_str(self):
        station_a = Station.objects.create(name="Kyiv", latitude=50.4, longitude=30.5)
        station_b = Station.objects.create(name="Lviv", latitude=49.8, longitude=24.0)
        route = Route.objects.create(source=station_a, destination=station_b, distance=540)
        self.assertEqual(str(route), "Kyiv → Lviv")

    def test_journey_str(self):
        train = create_train()
        journey = create_journey(train)
        self.assertIn("Kyiv", str(journey))
        self.assertIn("Lviv", str(journey))

    def test_order_str(self):
        order = create_order()
        self.assertIn("Order", str(order))
        self.assertIn(str(order.id), str(order))

    def test_ticket_str(self):
        train = create_train()
        journey = create_journey(train)
        order = create_order()
        ticket = Ticket.objects.create(journey=journey, order=order, cargo=1, seat=1)
        self.assertIn("wagon 1", str(ticket))
        self.assertIn("seat 1", str(ticket))


class TicketCleanUnsavedJourneyTest(TestCase):

    def test_clean_skips_validation_when_journey_has_no_id(self):
        train = create_train(cargo_num=5, places_in_cargo=10)
        station_a = Station.objects.create(name="Kyiv", latitude=50.4, longitude=30.5)
        station_b = Station.objects.create(name="Lviv", latitude=49.8, longitude=24.0)
        route = Route.objects.create(source=station_a, destination=station_b, distance=540)
        unsaved_journey = Journey(
            route=route,
            train=train,
            departure_date="2025-06-01T10:00:00Z",
            arrival_date="2025-06-01T18:00:00Z",
        )
        order = create_order()
        ticket = Ticket(journey=unsaved_journey, order=order, cargo=999, seat=999)
        ticket.clean()  # повинно пройти без помилок, бо journey.id == None


class JourneyCrewTest(TestCase):

    def setUp(self):
        self.train = create_train()
        self.journey = create_journey(self.train)

    def test_add_crew_to_journey(self):
        crew = create_crew()
        self.journey.crew.add(crew)
        self.assertIn(crew, self.journey.crew.all())

    def test_remove_crew_from_journey(self):
        crew = create_crew()
        self.journey.crew.add(crew)
        self.journey.crew.remove(crew)
        self.assertNotIn(crew, self.journey.crew.all())

    def test_journey_can_have_multiple_crew(self):
        crew1 = create_crew(first_name="John", last_name="Doe", role="Conductor")
        crew2 = create_crew(first_name="Jane", last_name="Smith", role="Driver")
        self.journey.crew.set([crew1, crew2])
        self.assertEqual(self.journey.crew.count(), 2)
