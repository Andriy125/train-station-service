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
