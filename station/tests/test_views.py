from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from station.models import (
    Station, Route, TrainType, Train, Crew, Journey, Order, Ticket
)

User = get_user_model()

STATION_LIST_URL = reverse("station-list")
ROUTE_LIST_URL = reverse("route-list")
TRAIN_TYPE_LIST_URL = reverse("traintype-list")
TRAIN_LIST_URL = reverse("train-list")
CREW_LIST_URL = reverse("crew-list")
JOURNEY_LIST_URL = reverse("journey-list")
ORDER_LIST_URL = reverse("order-list")
TICKET_LIST_URL = reverse("ticket-list")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_user(username="user@test.com", password="pass123", is_staff=False):
    return User.objects.create_user(
        username=username, password=password, is_staff=is_staff
    )


def make_station(name="Kyiv", lat=50.4, lon=30.5):
    return Station.objects.create(name=name, latitude=lat, longitude=lon)


def make_train_type(name="Intercity"):
    return TrainType.objects.create(name=name)


def make_train(name="Test Train", cargo_num=5, places_in_cargo=10, train_type=None):
    if train_type is None:
        train_type = make_train_type()
    return Train.objects.create(
        name=name,
        cargo_num=cargo_num,
        places_in_cargo=places_in_cargo,
        train_type=train_type,
    )


def make_crew(first_name="John", last_name="Doe", role="Conductor"):
    return Crew.objects.create(first_name=first_name, last_name=last_name, role=role)


def make_route(source, destination, distance=540):
    return Route.objects.create(source=source, destination=destination, distance=distance)


def make_journey(route, train, departure="2025-06-01T10:00:00Z", arrival="2025-06-01T18:00:00Z"):
    return Journey.objects.create(
        route=route, train=train, departure_date=departure, arrival_date=arrival
    )


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


# ---------------------------------------------------------------------------
# StationViewSet
# ---------------------------------------------------------------------------

class StationViewSetTest(APITestCase):

    def setUp(self):
        self.station = make_station()
        self.user = make_user()
        self.admin = make_user(username="admin@test.com", is_staff=True)

    def test_list_requires_authentication(self):
        res = self.client.get(STATION_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_accessible_by_authenticated_user(self):
        res = auth_client(self.user).get(STATION_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_retrieve_accessible_by_authenticated_user(self):
        url = reverse("station-detail", args=[self.station.id])
        res = auth_client(self.user).get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_forbidden_for_non_staff(self):
        data = {"name": "Odesa", "latitude": 46.5, "longitude": 30.7}
        res = auth_client(self.user).post(STATION_LIST_URL, data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_allowed_for_admin(self):
        data = {"name": "Odesa", "latitude": 46.5, "longitude": 30.7}
        res = auth_client(self.admin).post(STATION_LIST_URL, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Station.objects.count(), 2)

    def test_delete_allowed_for_admin(self):
        url = reverse("station-detail", args=[self.station.id])
        res = auth_client(self.admin).delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_forbidden_for_non_staff(self):
        url = reverse("station-detail", args=[self.station.id])
        res = auth_client(self.user).delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


# ---------------------------------------------------------------------------
# RouteViewSet
# ---------------------------------------------------------------------------

class RouteViewSetTest(APITestCase):

    def setUp(self):
        self.station_a = make_station(name="Kyiv")
        self.station_b = make_station(name="Lviv", lat=49.8, lon=24.0)
        self.route = make_route(self.station_a, self.station_b)
        self.user = make_user()
        self.admin = make_user(username="admin@test.com", is_staff=True)

    def test_list_forbidden_for_authenticated_non_staff(self):
        res = auth_client(self.user).get(ROUTE_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_forbidden_for_unauthenticated(self):
        res = self.client.get(ROUTE_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_accessible_by_admin(self):
        res = auth_client(self.admin).get(ROUTE_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_create_route_by_admin(self):
        station_c = make_station(name="Odesa", lat=46.5, lon=30.7)
        data = {
            "source_id": self.station_a.id,
            "destination_id": station_c.id,
            "distance": 475,
        }
        res = auth_client(self.admin).post(ROUTE_LIST_URL, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_retrieve_route_by_admin(self):
        url = reverse("route-detail", args=[self.route.id])
        res = auth_client(self.admin).get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.data["source"], dict)


# ---------------------------------------------------------------------------
# TrainTypeViewSet
# ---------------------------------------------------------------------------

class TrainTypeViewSetTest(APITestCase):

    def setUp(self):
        self.train_type = make_train_type()
        self.user = make_user()
        self.admin = make_user(username="admin@test.com", is_staff=True)

    def test_list_forbidden_for_non_staff(self):
        res = auth_client(self.user).get(TRAIN_TYPE_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_accessible_by_admin(self):
        res = auth_client(self.admin).get(TRAIN_TYPE_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_by_admin(self):
        res = auth_client(self.admin).post(TRAIN_TYPE_LIST_URL, {"name": "Express"})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# TrainViewSet
# ---------------------------------------------------------------------------

class TrainViewSetTest(APITestCase):

    def setUp(self):
        self.train_type = make_train_type()
        self.train = make_train(train_type=self.train_type)
        self.user = make_user()
        self.admin = make_user(username="admin@test.com", is_staff=True)

    def test_list_accessible_by_authenticated_user(self):
        res = auth_client(self.user).get(TRAIN_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_list_requires_authentication(self):
        res = self.client.get(TRAIN_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_forbidden_for_non_staff(self):
        data = {
            "name": "New Train",
            "cargo_num": 4,
            "places_in_cargo": 8,
            "train_type_id": self.train_type.id,
        }
        res = auth_client(self.user).post(TRAIN_LIST_URL, data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_allowed_for_admin(self):
        data = {
            "name": "New Train",
            "cargo_num": 4,
            "places_in_cargo": 8,
            "train_type_id": self.train_type.id,
        }
        res = auth_client(self.admin).post(TRAIN_LIST_URL, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_retrieve_returns_nested_train_type(self):
        url = reverse("train-detail", args=[self.train.id])
        res = auth_client(self.user).get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.data["train_type"], dict)


# ---------------------------------------------------------------------------
# CrewViewSet
# ---------------------------------------------------------------------------

class CrewViewSetTest(APITestCase):

    def setUp(self):
        self.crew = make_crew()
        self.user = make_user()
        self.admin = make_user(username="admin@test.com", is_staff=True)

    def test_list_forbidden_for_non_staff(self):
        res = auth_client(self.user).get(CREW_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_accessible_by_admin(self):
        res = auth_client(self.admin).get(CREW_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_create_crew_by_admin(self):
        data = {"first_name": "Jane", "last_name": "Smith", "role": "Driver"}
        res = auth_client(self.admin).post(CREW_LIST_URL, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_list_serializer_shows_full_name(self):
        res = auth_client(self.admin).get(CREW_LIST_URL)
        self.assertIn("full_name", res.data[0])
        self.assertNotIn("first_name", res.data[0])


# ---------------------------------------------------------------------------
# JourneyViewSet
# ---------------------------------------------------------------------------

class JourneyViewSetTest(APITestCase):

    def setUp(self):
        station_a = make_station(name="Kyiv")
        station_b = make_station(name="Lviv", lat=49.8, lon=24.0)
        self.route = make_route(station_a, station_b)
        self.train = make_train()
        self.journey = make_journey(self.route, self.train)
        self.user = make_user()
        self.admin = make_user(username="admin@test.com", is_staff=True)

    def test_list_accessible_without_authentication(self):
        res = self.client.get(JOURNEY_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_list_contains_available_seats(self):
        res = self.client.get(JOURNEY_LIST_URL)
        self.assertIn("available_seats", res.data[0])

    def test_create_forbidden_for_non_staff(self):
        data = {
            "route_id": self.route.id,
            "train_id": self.train.id,
            "crew_ids": [],
            "departure_date": "2025-08-01T10:00:00Z",
            "arrival_date": "2025-08-01T18:00:00Z",
        }
        res = auth_client(self.user).post(JOURNEY_LIST_URL, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_allowed_for_admin(self):
        crew = make_crew()
        data = {
            "route_id": self.route.id,
            "train_id": self.train.id,
            "crew_ids": [crew.id],
            "departure_date": "2025-08-01T10:00:00Z",
            "arrival_date": "2025-08-01T18:00:00Z",
        }
        res = auth_client(self.admin).post(JOURNEY_LIST_URL, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_filter_by_source(self):
        res = self.client.get(JOURNEY_LIST_URL, {"source": "Kyiv"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_filter_by_source_no_match(self):
        res = self.client.get(JOURNEY_LIST_URL, {"source": "Odesa"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 0)

    def test_filter_by_destination(self):
        res = self.client.get(JOURNEY_LIST_URL, {"destination": "Lviv"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_filter_by_train_type(self):
        res = self.client.get(JOURNEY_LIST_URL, {"train_type": "Intercity"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_retrieve_returns_nested_objects(self):
        url = reverse("journey-detail", args=[self.journey.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.data["route"], dict)
        self.assertIsInstance(res.data["train"], dict)

    def test_available_seats_decreases_after_ticket_sold(self):
        user = make_user(username="buyer@test.com")
        order = Order.objects.create(user=user)
        Ticket.objects.create(journey=self.journey, order=order, cargo=1, seat=1)

        res = self.client.get(JOURNEY_LIST_URL)
        total = self.train.cargo_num * self.train.places_in_cargo
        self.assertEqual(res.data[0]["available_seats"], total - 1)


# ---------------------------------------------------------------------------
# OrderViewSet
# ---------------------------------------------------------------------------

class OrderViewSetTest(APITestCase):

    def setUp(self):
        self.user = make_user()
        self.other_user = make_user(username="other@test.com")
        self.admin = make_user(username="admin@test.com", is_staff=True)

        station_a = make_station(name="Kyiv")
        station_b = make_station(name="Lviv", lat=49.8, lon=24.0)
        route = make_route(station_a, station_b)
        self.train = make_train()
        self.journey = make_journey(route, self.train)

        self.order = Order.objects.create(user=self.user)
        self.other_order = Order.objects.create(user=self.other_user)

    def test_list_requires_authentication(self):
        res = self.client.get(ORDER_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_sees_only_own_orders(self):
        res = auth_client(self.user).get(ORDER_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id"], self.order.id)

    def test_admin_sees_all_orders(self):
        res = auth_client(self.admin).get(ORDER_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_create_order_with_tickets(self):
        data = {
            "tickets": [
                {"journey": self.journey.id, "cargo": 1, "seat": 1}
            ]
        }
        res = auth_client(self.user).post(ORDER_LIST_URL, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.filter(user=self.user).count(), 2)

    def test_create_order_empty_tickets_fails(self):
        data = {"tickets": []}
        res = auth_client(self.user).post(ORDER_LIST_URL, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_duplicate_tickets_fails(self):
        data = {
            "tickets": [
                {"journey": self.journey.id, "cargo": 1, "seat": 1},
                {"journey": self.journey.id, "cargo": 1, "seat": 1},
            ]
        }
        res = auth_client(self.user).post(ORDER_LIST_URL, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_own_order(self):
        url = reverse("order-detail", args=[self.order.id])
        res = auth_client(self.user).get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("tickets", res.data)

    def test_retrieve_other_user_order_returns_404(self):
        url = reverse("order-detail", args=[self.other_order.id])
        res = auth_client(self.user).get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


# ---------------------------------------------------------------------------
# TicketViewSet
# ---------------------------------------------------------------------------

class TicketViewSetTest(APITestCase):

    def setUp(self):
        self.user = make_user()
        self.other_user = make_user(username="other@test.com")

        station_a = make_station(name="Kyiv")
        station_b = make_station(name="Lviv", lat=49.8, lon=24.0)
        route = make_route(station_a, station_b)
        self.train = make_train()
        self.journey = make_journey(route, self.train)

        self.order = Order.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(
            journey=self.journey, order=self.order, cargo=1, seat=1
        )
        self.other_order = Order.objects.create(user=self.other_user)
        self.other_ticket = Ticket.objects.create(
            journey=self.journey, order=self.other_order, cargo=1, seat=2
        )

    def test_list_requires_authentication(self):
        res = self.client.get(TICKET_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_sees_only_own_tickets(self):
        res = auth_client(self.user).get(TICKET_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id"], self.ticket.id)

    def test_retrieve_own_ticket(self):
        url = reverse("ticket-detail", args=[self.ticket.id])
        res = auth_client(self.user).get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_other_user_ticket_returns_404(self):
        url = reverse("ticket-detail", args=[self.other_ticket.id])
        res = auth_client(self.user).get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_ticket_directly_is_not_allowed(self):
        data = {"journey": self.journey.id, "cargo": 2, "seat": 1, "order": self.order.id}
        res = auth_client(self.user).post(TICKET_LIST_URL, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)