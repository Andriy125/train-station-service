from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample
)
from drf_spectacular.types import OpenApiTypes


# ─── Stations ────────────────────────────────────────────────────────────────

station_docs = {
    'list': extend_schema(
        tags=['Stations'],
        summary='List all stations',
        description='Returns a list of all railway stations with their names and coordinates.',
    ),
    'retrieve': extend_schema(
        tags=['Stations'],
        summary='Retrieve a station',
        description='Returns full details of a specific station including latitude and longitude.',
    ),
    'create': extend_schema(
        tags=['Stations'],
        summary='Create a station',
        description='Admin only. Creates a new railway station.',
        examples=[
            OpenApiExample(
                'Example',
                value={
                    'name': 'Kyiv-Pasazhyrskyi',
                    'latitude': 50.4404,
                    'longitude': 30.4869
                },
                request_only=True,
            )
        ],
    ),
    'update': extend_schema(tags=['Stations'], summary='Update a station'),
    'partial_update': extend_schema(tags=['Stations'], summary='Partially update a station'),
    'destroy': extend_schema(tags=['Stations'], summary='Delete a station'),
}


# ─── Routes ──────────────────────────────────────────────────────────────────

route_docs = {
    'list': extend_schema(
        tags=['Routes'],
        summary='List all routes',
        description='Returns a list of routes with source station, destination station, and distance.',
    ),
    'retrieve': extend_schema(
        tags=['Routes'],
        summary='Retrieve a route',
        description='Returns full details of a route including nested station objects.',
    ),
    'create': extend_schema(
        tags=['Routes'],
        summary='Create a route',
        description='Admin only. Creates a route between two different stations.',
        examples=[
            OpenApiExample(
                'Example',
                value={
                    'source_id': 1,
                    'destination_id': 2,
                    'distance': 540,
                },
                request_only=True,
            )
        ]
    ),
    'update': extend_schema(tags=['Routes'], summary='Update a route'),
    'partial_update': extend_schema(tags=['Routes'], summary='Partially update a route'),
    'destroy': extend_schema(tags=['Routes'], summary='Delete a route')
}


# ─── Train Types ─────────────────────────────────────────────────────────────

train_type_docs = {
    'list': extend_schema(
        tags=['Train Types'],
        summary='List all train types',
        description='Returns all available train types (e.g. Intercity, Regional, Night Train).',
    ),
    'retrieve': extend_schema(
        tags=['Train Types'],
        summary='Retrieve a train type'
    ),
    'create': extend_schema(
        tags=['Train Types'],
        summary='Create a train type',
        description='Admin only.',
        examples=[
            OpenApiExample(
                'Example',
                value={'name': 'Intercity'},
                request_only=True
            )
        ],
    ),
    'update': extend_schema(tags=['Train Types'], summary='Update a train type'),
    'partial_update': extend_schema(tags=['Train Types'], summary='Partially update a train type'),
    'destroy': extend_schema(tags=['Train Types'], summary='Delete a train type'),
}


# ─── Trains ──────────────────────────────────────────────────────────────────

train_docs = {
    'list': extend_schema(
        tags=['Trains'],
        summary='List all trains',
        description='Returns all trains with wagon count, seats per wagon and train type.',
    ),
    'retrieve': extend_schema(
        tags=['Trains'],
        summary='Retrieve a train',
        description='Returns full train details including nested train type.',
    ),
    'create': extend_schema(
        tags=['Trains'],
        summary='Create a train',
        description='Admin only. Creates a new train with seating configuration.',
        examples=[
            OpenApiExample(
                'Example',
                value={
                    'name': 'Intercity 747',
                    'cargo_num': 8,
                    'places_in_cargo': 54,
                    'train_type_id': 1
                },
                request_only=True,
            )
        ],
    ),
    'update': extend_schema(tags=['Trains'], summary='Update a train'),
    'partial_update': extend_schema(tags=['Trains'], summary='Partially update a train'),
    'destroy': extend_schema(tags=['Trains'], summary='Delete a train'),
}


# ─── Crew ────────────────────────────────────────────────────────────────────

crew_docs = {
    'list': extend_schema(
        tags=['Crew'],
        summary='List all crew members',
        description='Returns all crew members with their full name and role.',
    ),
    'retrieve': extend_schema(
        tags=['Crew'],
        summary='Retrieve a crew member',
    ),
    'create': extend_schema(
        tags=['Crew'],
        summary='Create a crew member',
        description='Admin only.',
        examples=[
            OpenApiExample(
                'Example',
                value={
                    'first_name': 'Ivan',
                    'last_name': 'Petrenko',
                    'role': 'Driver'
                },
                request_only=True,
            )
        ],
    ),
    'update': extend_schema(tags=['Crew'], summary='Update a crew member'),
    'partial_update': extend_schema(tags=['Crew'], summary='Partially update a crew member'),
    'destroy': extend_schema(tags=['Crew'], summary='Delete a crew member'),
}


# ─── Journeys ────────────────────────────────────────────────────────────────

journey_docs = {
    'list': extend_schema(
        tags=['Journeys'],
        summary='List all journeys',
        description=(
            'Returns available train journeys with route, train and crew info.\n'
            'Available filters:\n'
            '- source — station name (partial match)\n'
            '- destination — station name (partial match)\n'
            '- train_type — train type name\n'
            '- departure_date — exact date (YYYY-MM-DD)\n'
            '- departure_date__gte — from date\n'
            '- departure_date__lte — to date\n\n'
            'Example:\n'
            '/api/v1/station/journeys/?source=Kyiv&destination=Lviv&departure_date__gte=2025-06-01'
        ),
        parameters=[
            OpenApiParameter(
                name='source',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description=(
                    'Filter by source station name '
                    '(case-insensitive, partial match). '
                    'Example: `Kyiv`'
                ),
                required=False,
            ),
            OpenApiParameter(
                name='destination',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description=(
                    'Filter by destination station name '
                    '(case-insensitive, partial match). '
                    'Example: `Lviv`'
                ),
                required=False,
            ),
            OpenApiParameter(
                name='train_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description=(
                    'Filter by train type name '
                    '(case-insensitive, partial match). '
                    'Example: `Intercity`'
                ),
                required=False,
            ),
            OpenApiParameter(
                name='departure_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description=(
                    'Filter by exact departure date. '
                    'Format: `YYYY-MM-DD`'
                ),
                required=False,
            ),
            OpenApiParameter(
                name='departure_date__gte',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description=(
                    'Filter journeys departing on or after this date. '
                    'Format: `YYYY-MM-DD`'
                ),
                required=False,
            ),
            OpenApiParameter(
                name='departure_date__lte',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description=(
                    'Filter journeys departing on or before this date. '
                    'Format: `YYYY-MM-DD`'
                ),
                required=False,
            ),
        ],
    ),
    'retrieve': extend_schema(
        tags=['Journeys'],
        summary='Retrieve a journey',
        description='Returns full journey details including route, train configuration and assigned crew.',
    ),
    'create': extend_schema(
        tags=['Journeys'],
        summary='Create a journey',
        description='Admin only. Assigns a train and crew to a route for a specific departure and arrival date',
        examples=[
            OpenApiExample(
                'Example',
                value={
                    'route_id': 1,
                    'train_id': 2,
                    'crew_ids': [1, 3],
                    'departure_date': '2025-06-01',
                    'arrival_date': '2025-06-02',
                },
                request_only=True,
            )
        ],
    ),
    'update': extend_schema(tags=['Journeys'], summary='Update a journey'),
    'partial_update': extend_schema(tags=['Journeys'], summary='Partially update a journey'),
    'destroy': extend_schema(tags=['Journeys'], summary='Delete a journey'),
}


# ─── Orders ──────────────────────────────────────────────────────────────────

order_docs = {
    'list': extend_schema(
        tags=['Orders'],
        summary='List orders',
        description='Authenticated users see only their own orders. Staff can see all orders.',
    ),
    'retrieve': extend_schema(
        tags=['Orders'],
        summary='Retrieve an order',
        description='Returns order details with all associated tickets.',
    ),
    'create': extend_schema(
        tags=['Orders'],
        summary='Create an order',
        description=(
            'Creates an order with one or more tickets. '
            'Seat availability is validated in real time. '
            'All tickets are saved atomically '
            '— if any seat is taken, the whole order is rejected.'
        ),
        examples=[
            OpenApiExample(
                'Single ticket',
                value={
                    'tickets': [
                        {
                            'journey': 1,
                            'cargo': 2,
                            'seat': 14
                        }
                    ]
                },
                request_only=True,
            ),
            OpenApiExample(
                'Multiple tickets',
                value={
                    'tickets': [
                        {
                            'journey': 1,
                            'cargo': 1,
                            'seat': 5
                        },
                        {
                            'journey': 1,
                            'cargo': 1,
                            'seat': 6
                        },
                    ]
                },
                request_only=True,
            ),
        ],
    ),
    'update': extend_schema(tags=['Orders'], summary='Update an order'),
    'partial_update': extend_schema(tags=['Orders'], summary='Partially update an order'),
    'destroy': extend_schema(tags=['Orders'], summary='Delete an order'),
}


# ─── Tickets ─────────────────────────────────────────────────────────────────

ticket_docs = {
    'list': extend_schema(
        tags=['Tickets'],
        summary='List tickets',
        description='Returns all tickets belonging to the authenticated user.',
    ),
    'retrieve': extend_schema(
        tags=['Tickets'],
        summary='Retrieve a ticket',
        description='Returns ticket details including journey info and the associated order.',
    ),
    'create': extend_schema(
        tags=['Tickets'],
        summary='Create a ticket',
        description='Authenticated users can create tickets only for their own orders',
        examples=[
            OpenApiExample(
                'Example',
                value={
                    'journey': 1,
                    'cargo': 3,
                    'seat': 22,
                    'order': 1
                },
                request_only=True,
            )
        ],
    ),
    'update': extend_schema(tags=['Tickets'], summary='Update a ticket'),
    'partial_update': extend_schema(tags=['Tickets'], summary='Partially update a ticket'),
    'destroy': extend_schema(tags=['Tickets'], summary='Delete a ticket'),
}
