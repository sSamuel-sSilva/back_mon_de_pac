from .models import Travel, TravelBooking
from django.shortcuts import get_object_or_404


class TravelQuery:
    @staticmethod
    def get_bookings_by_travel(user, travel_id):
        travel = get_object_or_404(Travel.objects.select_related('destiny', 'bus'), pk=travel_id)

        queryset = TravelBooking.objects.select_related(
            "patient", "companion", "card", "vital_monitor_device"
        ).filter(travel=travel)

        if not user.is_staff:
            queryset = queryset.filter(patient__user=user)

        return {
            "travel": {
                "id": travel.pk,
                "destiny": str(travel.destiny),
                "origin": travel.bus.origin if hasattr(travel.bus, 'origin') else "Não informado",
                "date": travel.date,
                "time": travel.time,
                "vacations": travel.vacations,
                "status": travel.status,
                "status_display": travel.get_status_display()
            },
            "bookings": [
                {
                    "id": b.pk,
                    "patient": {
                        "id": b.patient.pk,
                        "name": b.patient.name
                    },
                    "companion": {
                        "id": b.companion.pk if b.companion else None,
                        "name": b.companion.name if b.companion else None
                    },
                    "need_vital_monitor_device": b.need_vital_monitor_device,
                    "status": b.status,
                    "status_display": b.get_status_display(),
                    "card": {
                        "id": b.card.pk if b.card else None,
                        "number": b.card.number if b.card else None
                    },
                    "vital_monitor_device": {
                        "id": b.vital_monitor_device.pk if b.vital_monitor_device else None,
                        "identifier": b.vital_monitor_device.identifier if b.vital_monitor_device else None
                    },
                    "observations": b.observations
                }
                for b in queryset
            ]
        }


class TravelBookingQuery:
    @staticmethod
    def get_travel_booking_detail(user, booking_id):
        queryset = TravelBooking.objects.select_related("travel", "patient", "companion", "card", "vital_monitor_device")
        if not user.is_staff:
            queryset = queryset.filter(patient__user=user)
        
        booking = get_object_or_404(queryset, id=booking_id)

        return {
            "id": booking.pk,
            "travel": {
                "id": booking.travel.pk,
                "origin": booking.travel.origin,
                "destination": booking.travel.destination,
                "date": booking.travel.date,
                "vacations": booking.travel.vacations
            },
            "patient": {
                "id": booking.patient.pk,
                "name": booking.patient.name
            },
            "companion": {
                "id": booking.companion.pk if booking.companion else None,
                "name": booking.companion.name if booking.companion else None
            },
            "need_vital_monitor_device": booking.need_vital_monitor_device,
            "status": booking.status,
            "card": {
                "id": booking.card.pk if booking.card else None,
                "number": booking.card.number if booking.card else None
            },
            "vital_monitor_device": {
                "id": booking.vital_monitor_device.pk if booking.vital_monitor_device else None,
                "identifier": booking.vital_monitor_device.identifier if booking.vital_monitor_device else None
            }
        }