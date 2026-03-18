# import django_filters
# from .models import TravelBooking

# class TravelBookingFilter(django_filters.FilterSet):
#     patient_name = django_filters.CharFilter(
#         field_name="patient__name",
#         lookup_expr="icontains"
#     )

#     class Meta:
#         model = TravelBooking
#         fields = ["travel", "status"]