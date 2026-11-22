from datetime import datetime

from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView, ListView, TemplateView, View

from .forms import AppointmentForm, ContactForm
from .models import (
    Appointment,
    BlogPost,
    FAQ,
    GalleryImage,
    Service,
    SiteSettings,
    Testimonial,
)
from .utils import available_slots, format_slot


def send_contact_email(contact_message):
    try:
        from django.core.mail import send_mail

        site = SiteSettings.load()
        if not site.email:
            return
        send_mail(
            subject=f"New contact message - {contact_message.subject or contact_message.name}",
            message=(
                f"Name: {contact_message.name}\n"
                f"Email: {contact_message.email}\n"
                f"Phone: {contact_message.phone}\n"
                f"Subject: {contact_message.subject or '-'}\n\n"
                f"{contact_message.message}"
            ),
            from_email=site.email,
            recipient_list=[site.email],
            fail_silently=True,
        )
    except Exception:
        pass


def send_appointment_email(appointment):
    try:
        from django.core.mail import send_mail

        site = SiteSettings.load()
        send_mail(
            subject=f"New appointment request — {appointment.name}",
            message=(
                f"Patient: {appointment.name}\n"
                f"Phone: {appointment.phone}\n"
                f"Email: {appointment.email}\n"
                f"Service: {appointment.service}\n"
                f"Date: {appointment.date} at {appointment.time:%H:%M}\n"
                f"Notes: {appointment.message or '—'}"
            ),
            from_email=site.email or None,
            recipient_list=[site.email] if site.email else [],
            fail_silently=True,
        )
    except Exception:
        pass


class HomeView(TemplateView):
    template_name = "clinic/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        featured = Service.objects.filter(is_featured=True)
        context["services"] = featured if featured.exists() else Service.objects.all()[:6]
        context["testimonials"] = Testimonial.objects.filter(is_published=True)[:6]
        context["posts"] = BlogPost.objects.filter(is_published=True)[:3]
        context["faqs"] = FAQ.objects.filter(is_published=True)[:4]
        context["gallery"] = GalleryImage.objects.filter(is_published=True)[:6]
        return context


class AboutView(TemplateView):
    template_name = "clinic/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["testimonials"] = Testimonial.objects.filter(is_published=True)[:3]
        return context


class ServiceListView(ListView):
    model = Service
    template_name = "clinic/services.html"
    context_object_name = "services"


class ServiceDetailView(DetailView):
    model = Service
    template_name = "clinic/service_detail.html"
    context_object_name = "service"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["related"] = Service.objects.exclude(pk=self.object.pk)[:3]
        context["testimonials"] = self.object.testimonials.filter(is_published=True)[:3]
        return context


class TestimonialListView(ListView):
    model = Testimonial
    template_name = "clinic/testimonials.html"
    context_object_name = "testimonials"

    def get_queryset(self):
        return Testimonial.objects.filter(is_published=True)


class GalleryListView(ListView):
    model = GalleryImage
    template_name = "clinic/gallery.html"
    context_object_name = "images"

    def get_queryset(self):
        return GalleryImage.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = (
            GalleryImage.objects.filter(is_published=True)
            .exclude(category="")
            .values_list("category", flat=True)
            .distinct()
        )
        return context


class BlogListView(ListView):
    model = BlogPost
    template_name = "clinic/blog.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True)


class BlogDetailView(DetailView):
    model = BlogPost
    template_name = "clinic/blog_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recent"] = (
            BlogPost.objects.filter(is_published=True).exclude(pk=self.object.pk)[:3]
        )
        return context


class FAQListView(ListView):
    model = FAQ
    template_name = "clinic/faq.html"
    context_object_name = "faqs"

    def get_queryset(self):
        return FAQ.objects.filter(is_published=True)


class ContactView(View):
    template_name = "clinic/contact.html"

    def get(self, request):
        return self.render(request, ContactForm())

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            send_contact_email(contact_message)
            messages.success(
                request, "Thank you! Your message has been received — we'll be in touch shortly."
            )
            return redirect("clinic:contact")
        return self.render(request, form)

    def render(self, request, form):
        from django.shortcuts import render

        return render(request, self.template_name, {"form": form})


class BookingView(View):
    template_name = "clinic/book.html"

    def get(self, request):
        initial = {}
        service_id = request.GET.get("service")
        if service_id and service_id.isdigit():
            initial["service"] = service_id
        return self.render(request, AppointmentForm(initial=initial))

    def post(self, request):
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.status = Appointment.STATUS_PENDING
            try:
                appointment.save()
            except IntegrityError:
                form.add_error(
                    None,
                    "Sorry, that time has just been taken. Please choose another slot.",
                )
                return self.render(request, form)
            send_appointment_email(appointment)
            request.session["last_appointment"] = appointment.pk
            return redirect("clinic:booking_success")
        return self.render(request, form)

    def render(self, request, form):
        from django.shortcuts import render

        services = Service.objects.all()
        return render(
            request,
            self.template_name,
            {"form": form, "services": services},
        )


class BookingSuccessView(TemplateView):
    template_name = "clinic/booking_success.html"

    def get(self, request, *args, **kwargs):
        pk = request.session.get("last_appointment")
        if not pk:
            return redirect("clinic:book")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.request.session.get("last_appointment")
        context["appointment"] = Appointment.objects.filter(pk=pk).first()
        return context


class SlotsApiView(View):
    def get(self, request):
        raw = request.GET.get("date", "")
        try:
            day = datetime.strptime(raw, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid date"}, status=400)

        if day < timezone.localdate():
            return JsonResponse({"error": "Date is in the past"}, status=400)

        slots = available_slots(day)
        return JsonResponse(
            {
                "date": raw,
                "closed": not slots,
                "slots": [{"value": s.strftime("%H:%M"), "label": format_slot(s)} for s in slots],
            }
        )


def robots_txt(request):
    sitemap_url = request.build_absolute_uri("/sitemap.xml")
    return HttpResponse(
        "User-agent: *\nAllow: /\n\nSitemap: " + sitemap_url + "\n",
        content_type="text/plain",
    )


def custom_404(request, exception):
    from django.shortcuts import render

    return render(request, "404.html", status=404)


def custom_500(request):
    from django.shortcuts import render

    return render(request, "500.html", status=500)
