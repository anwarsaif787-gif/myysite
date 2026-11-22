from datetime import time, timedelta

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import AppointmentForm
from .models import (
    Appointment,
    BlogPost,
    ContactMessage,
    DoctorProfile,
    FAQ,
    Service,
    SiteSettings,
    Testimonial,
)
from .utils import generate_slots


def next_open_day(days_ahead=3):
    """Return a future date that is not a Friday."""
    day = timezone.localdate() + timedelta(days=days_ahead)
    while day.weekday() == 4:
        day += timedelta(days=1)
    return day


def next_weekday(weekday):
    day = timezone.localdate() + timedelta(days=1)
    while day.weekday() != weekday:
        day += timedelta(days=1)
    return day


def next_friday():
    return next_weekday(4)


def next_sunday():
    return next_weekday(6)


class PageTests(TestCase):
    def setUp(self):
        self.service = Service.objects.create(
            name="Manual Therapy", short_description="Hands-on care", duration_minutes=45
        )
        Testimonial.objects.create(patient_name="Test Patient", rating=5, quote="Great.")
        FAQ.objects.create(question="Question?", answer="Answer.", order=1)
        BlogPost.objects.create(title="Test Post", content="Body", excerpt="Excerpt")

    def test_public_pages_render(self):
        urls = [
            reverse("clinic:home"),
            reverse("clinic:about"),
            reverse("clinic:services"),
            reverse("clinic:service_detail", args=[self.service.slug]),
            reverse("clinic:testimonials"),
            reverse("clinic:gallery"),
            reverse("clinic:blog"),
            reverse("clinic:blog_detail", args=["test-post"]),
            reverse("clinic:faq"),
            reverse("clinic:contact"),
            reverse("clinic:book"),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_sitemap_renders(self):
        self.assertEqual(self.client.get("/sitemap.xml").status_code, 200)


class SingletonTests(TestCase):
    def test_site_settings_is_singleton(self):
        first = SiteSettings.load()
        first.clinic_name = "Clinic A"
        first.save()
        second = SiteSettings.load()
        self.assertEqual(SiteSettings.objects.count(), 1)
        self.assertEqual(second.clinic_name, "Clinic A")

    def test_doctor_profile_singleton(self):
        DoctorProfile.load().save()
        DoctorProfile.load().save()
        self.assertEqual(DoctorProfile.objects.count(), 1)


class AppointmentFormTests(TestCase):
    def setUp(self):
        self.service = Service.objects.create(name="Assessment", duration_minutes=45)
        self.day = next_open_day()

    def payload(self, **overrides):
        data = {
            "service": self.service.pk,
            "date": self.day.isoformat(),
            "time": "09:00",
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "+91 98520 60649",
            "message": "",
            "website": "",
        }
        data.update(overrides)
        return data

    def test_valid_appointment_saves(self):
        form = AppointmentForm(data=self.payload())
        self.assertTrue(form.is_valid(), form.errors)
        appointment = form.save()
        self.assertEqual(appointment.status, Appointment.STATUS_PENDING)

    def test_past_date_is_rejected(self):
        past = (timezone.localdate() - timedelta(days=1)).isoformat()
        form = AppointmentForm(data=self.payload(date=past))
        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)

    def test_friday_is_rejected(self):
        form = AppointmentForm(data=self.payload(date=next_friday().isoformat()))
        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)

    def test_sunday_is_bookable(self):
        form = AppointmentForm(data=self.payload(date=next_sunday().isoformat()))
        self.assertTrue(form.is_valid(), form.errors)

    def test_double_booking_is_rejected(self):
        Appointment.objects.create(
            name="Existing",
            email="existing@example.com",
            phone="123",
            service=self.service,
            date=self.day,
            time=time(9, 0),
            status=Appointment.STATUS_CONFIRMED,
        )
        form = AppointmentForm(data=self.payload())
        self.assertFalse(form.is_valid())
        self.assertTrue(form.non_field_errors())

    def test_spam_honeypot_is_rejected(self):
        form = AppointmentForm(data=self.payload(website="http://spam.example"))
        self.assertFalse(form.is_valid())

    def test_time_outside_hours_is_rejected(self):
        form = AppointmentForm(data=self.payload(time="22:00"))
        self.assertFalse(form.is_valid())


class BookingViewTests(TestCase):
    def setUp(self):
        self.service = Service.objects.create(name="Assessment", duration_minutes=45)
        self.day = next_open_day()

    def test_booking_post_creates_appointment(self):
        response = self.client.post(
            reverse("clinic:book"),
            {
                "service": self.service.pk,
                "date": self.day.isoformat(),
                "time": "10:00",
                "name": "Jane Doe",
                "email": "jane@example.com",
                "phone": "123",
                "message": "",
                "website": "",
            },
        )
        self.assertRedirects(response, reverse("clinic:booking_success"))
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertIn("last_appointment", self.client.session)

    def test_booking_get_preselects_service(self):
        response = self.client.get(reverse("clinic:book") + f"?service={self.service.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'value="{self.service.pk}" selected')


class ContactViewTests(TestCase):
    def test_contact_message_saves(self):
        response = self.client.post(
            reverse("clinic:contact"),
            {
                "name": "Jane",
                "email": "jane@example.com",
                "phone": "123",
                "subject": "Hello",
                "message": "I would like to book.",
                "website": "",
            },
        )
        self.assertRedirects(response, reverse("clinic:contact"))
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_contact_honeypot_blocks_spam(self):
        self.client.post(
            reverse("clinic:contact"),
            {
                "name": "Bot",
                "email": "bot@example.com",
                "subject": "Spam",
                "message": "Buy now",
                "website": "http://spam.example",
            },
        )
        self.assertEqual(ContactMessage.objects.count(), 0)


class SlotsApiTests(TestCase):
    def test_returns_slots_for_open_day(self):
        day = next_open_day()
        response = self.client.get(reverse("clinic:api_slots"), {"date": day.isoformat()})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertGreater(len(payload["slots"]), 0)
        self.assertFalse(payload["closed"])

    def test_returns_closed_on_friday(self):
        response = self.client.get(
            reverse("clinic:api_slots"), {"date": next_friday().isoformat()}
        )
        payload = response.json()
        self.assertEqual(payload["slots"], [])
        self.assertTrue(payload["closed"])

    def test_returns_slots_on_sunday(self):
        response = self.client.get(
            reverse("clinic:api_slots"), {"date": next_sunday().isoformat()}
        )
        payload = response.json()
        self.assertGreater(len(payload["slots"]), 0)
        self.assertFalse(payload["closed"])

    def test_rejects_invalid_date(self):
        response = self.client.get(reverse("clinic:api_slots"), {"date": "not-a-date"})
        self.assertEqual(response.status_code, 400)

    def test_generate_slots_starts_and_ends_correctly(self):
        day = next_open_day()
        slots = generate_slots(day)
        self.assertEqual(slots[0], time(9, 0))
        self.assertEqual(slots[-1], time(16, 30))


class SeoTests(TestCase):
    def test_robots_txt_points_to_sitemap(self):
        response = self.client.get(reverse("clinic:robots"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertIn("Sitemap:", response.content.decode())
