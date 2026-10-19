from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from django.utils import timezone
from decimal import Decimal

class Vehicle(models.Model):
    FUEL_PETROL = 'Petrol'
    FUEL_DIESEL = 'Diesel'
    FUEL_ELECTRIC = 'Electric'
    FUEL_HYBRID = 'Hybrid'

    FUEL_CHOICES = [
        (FUEL_PETROL, 'Petrol'),
        (FUEL_DIESEL, 'Diesel'),
        (FUEL_ELECTRIC, 'Electric'),
        (FUEL_HYBRID, 'Hybrid'),
    ]

    name = models.CharField(max_length=100, help_text="Model name, e.g. Fortuner, Model 3")
    brand = models.CharField(max_length=100, help_text="Manufacturer brand, e.g. Toyota, Tesla")
    year = models.IntegerField(
        validators=[MinValueValidator(1900)],
        help_text="Manufacturing year"
    )
    price_per_day = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Rental rate per day in standard currency"
    )
    fuel_type = models.CharField(
        max_length=20, 
        choices=FUEL_CHOICES,
        help_text="Fuel type of vehicle"
    )
    is_available = models.BooleanField(
        default=True,
        help_text="Availability status for rent"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicles'

    def __str__(self):
        return f"{self.brand} {self.name} ({self.year}) - {self.fuel_type}"


class Booking(models.Model):
    # Phone validator for exactly 10 digits as specified in task rules
    phone_validator = RegexValidator(
        regex=r'^\d{10}$',
        message="Phone number must be exactly 10 digits."
    )

    vehicle = models.ForeignKey(
        Vehicle, 
        on_delete=models.CASCADE, 
        related_name='bookings'
    )
    customer_name = models.CharField(max_length=150)
    customer_phone = models.CharField(
        max_length=10, 
        validators=[phone_validator]
    )
    start_date = models.DateField()
    end_date = models.DateField()
    total_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        editable=False,
        help_text="Auto-calculated: days * price_per_day"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'

    def calculate_total_amount(self):
        """Calculates total_amount based on days * price_per_day."""
        if self.start_date and self.end_date and self.vehicle:
            days = (self.end_date - self.start_date).days
            if days > 0:
                return Decimal(days) * self.vehicle.price_per_day
        return Decimal('0.00')

    def save(self, *args, **kwargs):
        # Auto-compute total_amount prior to save
        if not self.total_amount:
            self.total_amount = self.calculate_total_amount()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking #{self.id} - {self.vehicle.name} for {self.customer_name} ({self.start_date} to {self.end_date})"
