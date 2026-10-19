from django.contrib import admin
from .models import Vehicle, Booking

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('id', 'brand', 'name', 'year', 'fuel_type', 'price_per_day', 'is_available')
    list_filter = ('brand', 'fuel_type', 'is_available', 'year')
    search_fields = ('name', 'brand')
    list_editable = ('is_available', 'price_per_day')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle', 'customer_name', 'customer_phone', 'start_date', 'end_date', 'total_amount', 'created_at')
    list_filter = ('start_date', 'end_date', 'vehicle__brand')
    search_fields = ('customer_name', 'customer_phone', 'vehicle__name')
    readonly_fields = ('total_amount', 'created_at')
