# Train Station Service API

API service for managing train journeys, routes, tickets and orders, written on DRF.

## Features

- JWT authenticated
- Admin panel `/admin/`
- Documentation is located at `/api/doc/swagger/`
- Managing stations, routes, train types and trains
- Managing crew members with roles
- Scheduling journeys with departure/arrival times
- Real-time available seats count per journey
- Creating orders with multiple tickets in a single request
- Ticket seat and cargo validation
- Filtering journeys by source, destination, train type and departure date
- Users can only view and manage their own orders and tickets

## DB Structure

<img width="771" height="628" alt="DB Structure" src="https://github.com/user-attachments/assets/10367e8d-167a-46b1-afc6-7832b42207d0" />


## Installing using GitHub

Install PostgreSQL and create a database, then:

```bash
git clone https://github.com/Andriy125/train-station-service.git
cd train_station_service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Set environment variables:

```bash
set POSTGRES_DB=train_station
set POSTGRES_USER=postgres
set POSTGRES_PASSWORD=postgres
set POSTGRES_HOST=localhost
set POSTGRES_PORT=5432
set SECRET_KEY=your-secret-key
```

```bash
python manage.py migrate
python manage.py runserver
```

## Run with Docker

Docker and Docker Compose must be installed.

Create a `.env` file in the project root:

```env
POSTGRES_DB=train_station
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
SECRET_KEY=your-secret-key
```

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8001` — opens Swagger UI automatically.

## Getting Access

1. Register a new user: `POST /api/user/register/`
2. Get access token: `POST /api/user/token/`
3. Refresh token: `POST /api/user/token/refresh/`

Use the access token in the `Authorization` header:

```
Authorization: Bearer <your_token>
```

Or click **Authorize** in Swagger UI and paste the token directly.

## API Documentation

Interactive Swagger UI:

```
http://localhost:8001/api/doc/swagger/
```

ReDoc:

```
http://localhost:8001/api/doc/redoc/
```

## API Endpoints

| Endpoint | Methods | Access |
|---|---|---|
| `/api/station/stations/` | GET, POST, PUT, DELETE | GET: authenticated, rest: admin |
| `/api/station/routes/` | GET, POST, PUT, DELETE | admin only |
| `/api/station/trains/` | GET, POST, PUT, DELETE | GET: authenticated, rest: admin |
| `/api/station/train-types/` | GET, POST, PUT, DELETE | admin only |
| `/api/station/crews/` | GET, POST, PUT, DELETE | admin only |
| `/api/station/journeys/` | GET, POST, PUT, DELETE | GET: public, rest: admin |
| `/api/station/orders/` | GET, POST | authenticated (own orders only) |
| `/api/station/tickets/` | GET | authenticated (own tickets only) |

### Journey Filters

| Parameter | Description |
|---|---|
| `source` | Filter by source station name (case-insensitive) |
| `destination` | Filter by destination station name (case-insensitive) |
| `train_type` | Filter by train type name (case-insensitive) |
| `departure_date` | Filter by exact date |
| `departure_date__gte` | Journeys departing from this date |
| `departure_date__lte` | Journeys departing up to this date |

## Running Tests

With Docker:

```bash
docker-compose run --rm web python manage.py test station.tests
```

Without Docker (requires local PostgreSQL running with env variables set):

```bash
python manage.py test station.tests
```
