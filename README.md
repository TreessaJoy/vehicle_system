# Vehicle Inventory & Booking REST API

**Candidate Task Submission for AI and Python Django Intern Position at Vynzora Pvt. Ltd.**

A robust, production-ready REST API built with **Django REST Framework (DRF)** implementing vehicle fleet management, strict booking validations, overlap prevention, automated pricing calculations, and interactive OpenAPI/Swagger documentation.

---

## 🚀 Live Demo & Video Walkthrough

- **Live Deployed API:** [https://vynzora-vehicle-api.onrender.com/api/docs/](https://vynzora-vehicle-api.onrender.com/api/docs/) 
- **Screen Recording Walkthrough (2-5 mins):** https://drive.google.com/drive/folders/1X3uafLf2qELDTmfXQOc8A-_JRHlC4MWH?usp=sharing

---

## 🛠️ Tech Stack
- **Framework:** Python 3.11+, Django 5.x, Django REST Framework (DRF)
- **Filtering & Search:** django-filter
- **Documentation:** OpenAPI 3.0 via drf-spectacular (Swagger UI & ReDoc)
- **Production Server:** Gunicorn + WhiteNoise
- **Database:** SQLite (local development) / PostgreSQL (production)

---

## 📦 Project Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/vehicle_system.git
cd vehicle_system
```

### 2. Create and Activate Virtual Environment
```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
```bash
cp .env.example .env
```

### 5. Run Database Migrations
```bash
python manage.py makemigrations inventory
python manage.py migrate
```

### 6. Create Superuser (Optional - for Django Admin)
```bash
python manage.py createsuperuser
```

### 7. Run Development Server
```bash
python manage.py runserver
```
The server will start at `http://127.0.0.1:8000/`.

---

## 🧪 Running Automated Tests
Run the comprehensive test suite verifying all 6 real-life business rules:
```bash
python manage.py test inventory --verbosity=2
```

---

## 📖 API Documentation & Endpoints

Interactive Swagger UI is available at:
👉 **`http://127.0.0.1:8000/api/docs/`**

### Vehicle Endpoints
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/vehicles/` | List all vehicles (supports filtering) |
| `POST` | `/api/vehicles/` | Add new vehicle |
| `GET` | `/api/vehicles/<id>/` | Retrieve vehicle details |
| `PUT` | `/api/vehicles/<id>/` | Update vehicle details |
| `DELETE` | `/api/vehicles/<id>/` | Remove vehicle |

#### Filtering Examples:
- `/api/vehicles/?brand=Toyota`
- `/api/vehicles/?fuel_type=Electric`
- `/api/vehicles/?is_available=true`
- Combined: `/api/vehicles/?brand=Tesla&is_available=true`

### Booking Endpoints
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/bookings/` | List all bookings |
| `POST` | `/api/bookings/` | Create new booking (with strict validation) |
| `GET` | `/api/bookings/<id>/` | Retrieve booking details |

---

## ⚖️ Real-Life Business Rules Implemented
1. **Double-Booking Prevention:** A vehicle cannot have overlapping bookings. If dates collide, returns `HTTP 400 Bad Request` with clear explanation.
2. **Automated Pricing Calculation:** `total_amount = days * price_per_day` auto-calculated server-side.
3. **Date Validations:**
   - `start_date` cannot be in the past.
   - `end_date` must be strictly greater than `start_date`.
4. **Phone Validation:** `customer_phone` must be exactly 10 digits (`^\d{10}$`).
5. **Availability State Transition:** Once booked, `vehicle.is_available` is automatically updated to `False`.

---

## 📝 Sample JSON Payloads

### 1. Create Vehicle (`POST /api/vehicles/`)
```json
{
  "name": "Fortuner Legender",
  "brand": "Toyota",
  "year": 2024,
  "price_per_day": "120.00",
  "fuel_type": "Diesel",
  "is_available": true
}
```

### 2. Create Booking (`POST /api/bookings/`)
```json
{
  "vehicle": 1,
  "customer_name": "Joy Kannadan",
  "customer_phone": "9876543210",
  "start_date": "2026-10-25",
  "end_date": "2026-10-28"
}
```

### 3. Response on Successful Booking (`HTTP 201 Created`)
```json
{
  "id": 1,
  "vehicle": 1,
  "vehicle_details": {
    "id": 1,
    "name": "Fortuner Legender",
    "brand": "Toyota",
    "year": 2024,
    "price_per_day": "120.00",
    "fuel_type": "Diesel",
    "is_available": false
  },
  "customer_name": "Joy Kannadan",
  "customer_phone": "9876543210",
  "start_date": "2026-10-25",
  "end_date": "2026-10-28",
  "total_amount": "360.00",
  "created_at": "2026-10-19 10:30:00"
}
```
