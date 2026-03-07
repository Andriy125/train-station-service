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
        on_delete=models.CASCADE,
        related_name='routes_from',
    )
    destination = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
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
        on_delete=models.CASCADE,
        related_name='trains',
    )

    def __str__(self):
        return self.name


class Crew(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"


class Journey(models.Model):
    id = models.AutoField(primary_key=True)
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name='journeys',
    )
    train = models.ForeignKey(
        Train,
        on_delete=models.CASCADE,
        related_name='journeys',
    )
    departure_date = models.DateField()
    arrival_date = models.DateField()

    crew = models.ManyToManyField(
        Crew,
        related_name='journeys',
    )

    def clean(self):
        if self.departure_date < self.arrival_date:
            raise ValidationError("Departure date must be before arrival date.")

    def __str__(self):
        return f"{self.route} {self.departure_date}"