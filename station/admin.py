from django.contrib import admin
from .models import (
    Station,
    Route
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