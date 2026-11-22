from django.urls import path

from . import views

app_name = "clinic"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("services/", views.ServiceListView.as_view(), name="services"),
    path("services/<slug:slug>/", views.ServiceDetailView.as_view(), name="service_detail"),
    path("testimonials/", views.TestimonialListView.as_view(), name="testimonials"),
    path("gallery/", views.GalleryListView.as_view(), name="gallery"),
    path("blog/", views.BlogListView.as_view(), name="blog"),
    path("blog/<slug:slug>/", views.BlogDetailView.as_view(), name="blog_detail"),
    path("faq/", views.FAQListView.as_view(), name="faq"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("book/", views.BookingView.as_view(), name="book"),
    path("book/success/", views.BookingSuccessView.as_view(), name="booking_success"),
    path("api/slots/", views.SlotsApiView.as_view(), name="api_slots"),
    path("robots.txt", views.robots_txt, name="robots"),
]
