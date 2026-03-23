import django_filters
from station.models import Journey


class JourneyFilter(django_filters.FilterSet):

    source = django_filters.CharFilter(
        field_name='route__source__name',
        lookup_expr='icontains',
        label='Source station name',
    )

    destination = django_filters.CharFilter(
        field_name='route__destination__name',
        lookup_expr='icontains',
        label="Destination station name"
    )

    train_type = django_filters.CharFilter(
        field_name='train__train_type__name',
        lookup_expr='icontains',
        label='Train type',
    )

    class Meta:
        model = Journey
        fields = {
            "departure_date": ["exact", "gte", "lte"],
        }
