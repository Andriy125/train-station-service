from django.contrib import admin
from .models import (
    Station,
    Route,
    Journey,
    Crew,
    Train,
    TrainType
)


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "latitude",
        "longitude",
    )
    search_fields = ("name",)

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = (
        "source",
        "destination",
        "distance",
    )
    list_filter = (
        "source",
        "destination",
    )
    search_fields = (
        "source__name",
        "destination__name",
    )

@admin.register(Journey)
class JourneyAdmin(admin.ModelAdmin):
    list_display = (
        "route",
        "train",
        "departure_date",
        "arrival_date",
    )
    list_filter = (
        "route",
        "train",
        "departure_date",
        "arrival_date",
    )
    search_fields = (
        "route__source__name",
        "route__destination__name",
        "train__name",
        "departure_date",
        "arrival_date",
    )

@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "role",
    )

@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "cargo_num",
        "places_in_cargo",
        "train_type"
    )
    list_filter = (
        "name",
        "cargo_num",
        "places_in_cargo",
        "train_type"
    )
    search_fields = (
        "^name",
        "^train_type__name"
    )

@admin.register(TrainType)
class TrainTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
    )
    list_filter = (
        "name",
    )
    search_fields = (
        "name",
    )
