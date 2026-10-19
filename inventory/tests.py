from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Vehicle, Booking

class VehicleAPITests(APITestCase):
    def setUp(self):
        self.vehicle_toyota = Vehicle.objects.create(
            name="Fortuner",
            brand="Toyota",
            year=2023,
            price_per_day=Decimal("120.00"),
            fuel_type="Diesel",
            is_available=True
        )
        self.vehicle_tesla = Vehicle.objects.create(
            name="Model 3",
            brand="Tesla",
            year=2024,
            price_per_day=Decimal("150.00"),
            fuel_type="Electric",
            is_available=True
        )
        self.vehicle_unavailable = Vehicle.objects.create(
            name="Innova",
            brand="Toyota",
            year=2021,
            price_per_day=Decimal("90.00"),
            fuel_type="Petrol",
            is_available=False
        )

    def test_list_vehicles(self):
        url = reverse('vehicle-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_filter_vehicles_by_brand(self):
        url = f"{reverse('vehicle-list')}?brand=Toyota"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_filter_vehicles_by_fuel_type(self):
        url = f"{reverse('vehicle-list')}?fuel_type=Electric"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], "Model 3")

    def test_filter_vehicles_by_is_available(self):
        url = f"{reverse('vehicle-list')}?is_available=true"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_create_vehicle(self):
        url = reverse('vehicle-list')
        data = {
            "name": "Nexon EV",
            "brand": "Tata",
            "year": 2023,
            "price_per_day": "75.00",
            "fuel_type": "Electric",
            "is_available": True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vehicle.objects.count(), 4)


class BookingAPITests(APITestCase):
    def setUp(self):
        self.vehicle = Vehicle.objects.create(
            name="Fortuner",
            brand="Toyota",
            year=2023,
            price_per_day=Decimal("100.00"),
            fuel_type="Diesel",
            is_available=True
        )
        self.today = timezone.now().date()

    def test_successful_booking_and_auto_calc(self):
        """Rule: total_amount = days * price_per_day (auto-calc) & vehicle becomes unavailable"""
        url = reverse('booking-list')
        start = self.today + timedelta(days=2)
        end = self.today + timedelta(days=5) # 3 days rental
        data = {
            "vehicle": self.vehicle.id,
            "customer_name": "Joy Kannadan",
            "customer_phone": "9876543210", # 10 digits
            "start_date": str(start),
            "end_date": str(end)
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check calculation: 3 days * $100 = $300.00
        self.assertEqual(Decimal(str(response.data['total_amount'])), Decimal("300.00"))

        # Rule: After booking, vehicle becomes unavailable
        self.vehicle.refresh_from_db()
        self.assertFalse(self.vehicle.is_available)

    def test_double_booking_prevention(self):
        """Rule: Vehicle cannot be double-booked (no overlapping dates)"""
        url = reverse('booking-list')
        start = self.today + timedelta(days=5)
        end = self.today + timedelta(days=10)

        # First booking succeeds
        Booking.objects.create(
            vehicle=self.vehicle,
            customer_name="First Customer",
            customer_phone="9876543210",
            start_date=start,
            end_date=end,
            total_amount=Decimal("500.00")
        )

        # Attempt overlapping booking (e.g. days 7 to 12)
        data = {
            "vehicle": self.vehicle.id,
            "customer_name": "Second Customer",
            "customer_phone": "9123456789",
            "start_date": str(self.today + timedelta(days=7)),
            "end_date": str(self.today + timedelta(days=12))
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_start_date_in_past_rejected(self):
        """Rule: Start date cannot be in the past"""
        url = reverse('booking-list')
        data = {
            "vehicle": self.vehicle.id,
            "customer_name": "Test User",
            "customer_phone": "9876543210",
            "start_date": str(self.today - timedelta(days=2)), # Past date
            "end_date": str(self.today + timedelta(days=3))
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("start_date", response.data)

    def test_end_date_must_be_after_start_date(self):
        """Rule: End date must be after start date"""
        url = reverse('booking-list')
        data = {
            "vehicle": self.vehicle.id,
            "customer_name": "Test User",
            "customer_phone": "9876543210",
            "start_date": str(self.today + timedelta(days=5)),
            "end_date": str(self.today + timedelta(days=4)) # Before start date
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("end_date", response.data)

    def test_invalid_phone_number_rejected(self):
        """Rule: Phone number must be 10 digits"""
        url = reverse('booking-list')
        data = {
            "vehicle": self.vehicle.id,
            "customer_name": "Test User",
            "customer_phone": "98765", # Only 5 digits
            "start_date": str(self.today + timedelta(days=2)),
            "end_date": str(self.today + timedelta(days=4))
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("customer_phone", response.data)
