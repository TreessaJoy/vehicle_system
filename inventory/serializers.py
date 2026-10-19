from rest_framework import serializers
from django.utils import timezone
from django.db import transaction
import re
from decimal import Decimal
from .models import Vehicle, Booking

class VehicleSerializer(serializers.ModelSerializer):
    """
    Serializer for Vehicle model with full CRUD support.
    """
    class Meta:
        model = Vehicle
        fields = [
            'id', 
            'name', 
            'brand', 
            'year', 
            'price_per_day', 
            'fuel_type', 
            'is_available', 
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_year(self, value):
        current_year = timezone.now().year + 1
        if value < 1900 or value > current_year:
            raise serializers.ValidationError(f"Year must be between 1900 and {current_year}.")
        return value

    def validate_price_per_day(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price per day must be greater than zero.")
        return value


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for Booking with all Real-Life Business Logic:
    1. Phone number must be 10 digits
    2. Start date cannot be in the past
    3. End date must be after start date
    4. Vehicle cannot be double-booked (no overlapping dates)
    5. total_amount = days * price_per_day (auto-calc)
    6. After booking, vehicle becomes unavailable
    """
    vehicle_details = VehicleSerializer(source='vehicle', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id',
            'vehicle',
            'vehicle_details',
            'customer_name',
            'customer_phone',
            'start_date',
            'end_date',
            'total_amount',
            'created_at',
        ]
        read_only_fields = ['id', 'total_amount', 'created_at']

    def validate_customer_phone(self, value):
        # Rule: Phone number must be 10 digits
        clean_phone = value.strip()
        if not re.match(r'^\d{10}$', clean_phone):
            raise serializers.ValidationError("Phone number must be exactly 10 digits.")
        return clean_phone

    def validate(self, attrs):
        vehicle = attrs.get('vehicle')
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        today = timezone.now().date()

        # Rule: Start date cannot be in the past
        if start_date and start_date < today:
            raise serializers.ValidationError({
                "start_date": "Start date cannot be in the past."
            })

        # Rule: End date must be after start date
        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError({
                "end_date": "End date must be after start date."
            })

        # Rule: Vehicle cannot be double-booked (no overlapping dates)
        if vehicle and start_date and end_date:
            overlapping_query = Booking.objects.filter(
                vehicle=vehicle,
                start_date__lte=end_date,
                end_date__gte=start_date
            )
            
            # If updating an existing booking, exclude current instance
            if self.instance:
                overlapping_query = overlapping_query.exclude(pk=self.instance.pk)

            if overlapping_query.exists():
                raise serializers.ValidationError({
                    "non_field_errors": [
                        "Vehicle cannot be double-booked for overlapping dates. This vehicle is already reserved for the selected timeframe."
                    ]
                })

        return attrs

    def create(self, validated_data):
        """
        Creates booking inside an atomic transaction:
        - Calculates total_amount = days * price_per_day
        - Marks vehicle.is_available = False
        """
        vehicle = validated_data['vehicle']
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']

        # Rule: total_amount = days * price_per_day (auto-calc)
        days = (end_date - start_date).days
        total_amount = Decimal(days) * vehicle.price_per_day

        with transaction.atomic():
            booking = Booking.objects.create(
                total_amount=total_amount,
                **validated_data
            )

            # Rule: After booking, vehicle becomes unavailable
            vehicle.is_available = False
            vehicle.save(update_fields=['is_available'])

        return booking
