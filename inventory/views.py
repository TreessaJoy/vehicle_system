from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Vehicle, Booking
from .serializers import VehicleSerializer, BookingSerializer

class VehicleViewSet(viewsets.ModelViewSet):
    """
    API Endpoints for Vehicle Management:
    - GET /api/vehicles/ -> List vehicles (with filter support)
    - POST /api/vehicles/ -> Add new vehicle
    - GET /api/vehicles/<id>/ -> Vehicle details
    - PUT /api/vehicles/<id>/ -> Update vehicle
    - DELETE /api/vehicles/<id>/ -> Delete vehicle

    Supported Filters:
    - /api/vehicles/?brand=Toyota
    - /api/vehicles/?fuel_type=Electric
    - /api/vehicles/?is_available=true
    """
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'brand': ['exact', 'icontains'],
        'fuel_type': ['exact'],
        'is_available': ['exact'],
        'year': ['exact', 'gte', 'lte'],
    }
    search_fields = ['name', 'brand']
    ordering_fields = ['price_per_day', 'year', 'created_at']
    ordering = ['-id']


class BookingViewSet(viewsets.ModelViewSet):
    """
    API Endpoints for Booking:
    - GET /api/bookings/ -> List bookings
    - POST /api/bookings/ -> Create booking (handles all business logic & validations)
    - GET /api/bookings/<id>/ -> Booking details
    """
    queryset = Booking.objects.select_related('vehicle').all()
    serializer_class = BookingSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['vehicle', 'customer_phone', 'start_date', 'end_date']
    ordering = ['-created_at']

    # As per specification, only GET, POST, and GET <id> are required
    http_method_names = ['get', 'post', 'head', 'options']
