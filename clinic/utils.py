from datetime import datetime, time, timedelta

from django.utils import timezone

from .models import Appointment

OPEN_TIME = time(9, 0)
CLOSE_TIME = time(17, 0)
SLOT_INTERVAL_MINUTES = 30
CLOSED_WEEKDAYS = {4}  # Friday (Monday == 0)


def generate_slots(day):
    """Return every bookable slot start time for a given date."""
    if day.weekday() in CLOSED_WEEKDAYS:
        return []
    slots = []
    cursor = datetime.combine(day, OPEN_TIME)
    end = datetime.combine(day, CLOSE_TIME)
    while cursor < end:
        slots.append(cursor.time())
        cursor += timedelta(minutes=SLOT_INTERVAL_MINUTES)
    return slots


def booked_slots(day):
    return set(
        Appointment.objects.filter(
            date=day, status__in=[Appointment.STATUS_PENDING, Appointment.STATUS_CONFIRMED]
        ).values_list("time", flat=True)
    )


def available_slots(day):
    """Slots that are in the future and not already booked."""
    now = timezone.localtime()
    taken = booked_slots(day)
    result = []
    for slot in generate_slots(day):
        if slot in taken:
            continue
        if day == now.date() and slot <= now.time():
            continue
        if day < now.date():
            continue
        result.append(slot)
    return result


def format_slot(value):
    return value.strftime("%I:%M %p").lstrip("0")
