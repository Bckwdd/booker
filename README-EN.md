# 🎫 Event Booking Service API

RESTful API service for creating events and booking seats. Built with **Django REST Framework**.

## 🚀 Features

* **Users:** Registration and login (JWT Token).
* **Events:** Create events, view the list with optimized free-seats calculation.
* **Booking:**
    * Book seats for an event.
    * Protection against double booking.
* **My Dashboard:** View your created events and booking history.

## 📡 API Endpoints

## 📘 API Documentation

Interactive Swagger UI:
👉 http://127.0.0.1:8000/api/docs/


**Base URL:** `/api/v1/`

All requests to protected routes (🔒) must include:

### 🔐 Authentication (Users)

| Method | Endpoint | Request Body (JSON) | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/users/register/` | `{"email": "...", "username": "...", "password": "..."}` | Register a new user |
| `POST` | `/users/login/` | `{"email": "...", "password": "..."}` | Login (returns `access` & `refresh` tokens) |

---

### 📅 Events

| Method | Endpoint | Body / Params | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/events/` | — | 🔒 Get list of all events (includes `seats_taken`) |
| `POST` | `/events/` | `{"title": "...", "datetime": "...", "max_seats": 10}` | 🔒 Create a new event |
| `POST` | `/events/{id}/book/` | `{"seats_booked": 1}` | 🔒 Book a seat |

---

### 👤 My Dashboard

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/my/events/` | 🔒 Events created by the current user |
| `GET` | `/my/bookings/` | 🔒 User’s active bookings (with event details) |

---

### 📚 Documentation

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/docs/` | Interactive **Swagger UI** |
| `GET` | `/api/schema/` | Download OpenAPI schema (YAML) |

---

## 🛠 Tech Stack

* **Python 3.12+**
* **Django 5.x** & **Django REST Framework**
* **PostgreSQL**
* **SimpleJWT**
* **drf-spectacular**
* **python-decouple**
* **Ruff** (linter & formatter)

---

## 📂 Project Structure

```text
.
├── docker-compose.yml          # Run configuration (generated from example)
├── postgresql-db               # DB configuration
│   ├── data                    # Database files
│   └── .pg-env                 # Environment variables for Postgres
└── src                         # Source code
    ├── api                     # Django config
    ├── events                  # Events & bookings app
    ├── users                   # Users app
    ├── Dockerfile
    ├── docker-compose-example.yml
    ├── .env                    # Environment variables
    ├── manage.py
    └── ...
```

## ⚙️ Installation & Setup

## 1. Clone the repository

```bash
git clone <your-repo-url>
cd booker
```

All project code must be inside the ./src directory.

## 2. Prepare the Database

```bash
mkdir -p postgresql-db/data
```

Create file `postgresql-db/.pg-env`:

```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=eventsdb
```

### 3. Configure .env

Inside the `src` folder create` .env`:
```ini
DEBUG=True
SECRET_KEY=change-me-in-production

DB_HOST=booker-db
DB_PORT=5432
DB_NAME=eventsdb
DB_USER=postgres
DB_PASSWORD=password


JWT_ACCESS_MINUTES=60
JWT_REFRESH_DAYS=7
```

### 4. Create docker-compose.yml

In the root directory (above `src`) copy the example:

```bash
cp src/docker-compose-example.yml docker-compose.yml
```

### 5. Start Containers

```bash
docker-compose up --build -d
```

## 🧪 Testing & Code Quality

### Run tests

```bash
docker-compose exec booker-web python manage.py test
```

### Run Ruff linter

```bash
docker-compose exec booker-web ruff check .
```

