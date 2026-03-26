from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


class Station(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class Route(models.Model):
    id = models.AutoField(primary_key=True)
    source = models.ForeignKey(
        Station,
        on_delete=models.PROTECT,
        related_name='routes_from',
    )
    destination = models.ForeignKey(
        Station,
        on_delete=models.PROTECT,
        related_name='routes_to',
    )
    distance = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['source', 'destination'],
                name="unique_route"
            )
        ]

    def clean(self):
        self._validate_source_differs_from_destination()

    def _validate_source_differs_from_destination(self):
        if self.source == self.destination:
            raise ValidationError("Source and destination must be different.")

    def __str__(self):
        return f"{self.source} → {self.destination}"


class TrainType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Train(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    cargo_num = models.PositiveIntegerField()
    places_in_cargo = models.PositiveIntegerField()
    train_type = models.ForeignKey(
        TrainType,
        on_delete=models.PROTECT,
        related_name='trains',
    )

    def __str__(self):
        return self.name


class Crew(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.full_name} ({self.role})"


class Journey(models.Model):
    id = models.AutoField(primary_key=True)
    route = models.ForeignKey(
        Route,
        on_delete=models.PROTECT,
        related_name='journeys',
    )
    train = models.ForeignKey(
        Train,
        on_delete=models.PROTECT,
        related_name='journeys',
    )
    departure_date = models.DateTimeField()
    arrival_date = models.DateTimeField()

    crew = models.ManyToManyField(
        Crew,
        related_name='journeys',
    )

    def clean(self):
        self._validate_departure_before_arrival()

    def _validate_departure_before_arrival(self):
        if self.departure_date > self.arrival_date:
            raise ValidationError("Departure date must be before arrival date.")

    def __str__(self):
        return f"{self.route} {self.departure_date}"


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    def __str__(self):
        return f"Order {self.id} ({self.user})"


class Ticket(models.Model):
    id = models.AutoField(primary_key=True)
    cargo = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    journey = models.ForeignKey(
        Journey,
        on_delete=models.CASCADE,
        related_name='tickets',
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='tickets',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["journey", "cargo", "seat"],
                name="unique_ticket_for_journey"
            )
        ]

    def clean(self):
        if not self.journey.id:
            return

        train = self.journey.train
        self._validate_cargo(train)
        self._validate_seat(train)

    def _validate_cargo(self, train):
        if self.cargo < 1 or self.cargo > train.cargo_num:
            raise ValidationError(
                f"Cargo must be between 1 and {train.cargo_num}."
            )

    def _validate_seat(self, train):
        if self.seat < 1 or self.seat > train.places_in_cargo:
            raise ValidationError(
                f"Seat must be between 1 and {train.places_in_cargo}."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.journey} | wagon {self.cargo} seat {self.seat}"
