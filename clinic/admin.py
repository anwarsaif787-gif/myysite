from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Appointment,
    BlogPost,
    ContactMessage,
    DoctorProfile,
    FAQ,
    GalleryImage,
    Service,
    SiteSettings,
    Testimonial,
)


class SingletonAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdmin):
    fieldsets = (
        ("Brand", {"fields": ("clinic_name", "doctor_name", "tagline")}),
        ("Contact", {"fields": ("phone", "whatsapp", "email")}),
        (
            "Location",
            {
                "fields": (
                    "address",
                    "location_short",
                    "directions_url",
                    "map_embed_url",
                    "working_hours",
                )
            },
        ),
        ("Social", {"fields": ("facebook", "instagram", "linkedin", "youtube")}),
        ("Homepage", {"fields": ("hero_heading", "hero_subheading", "hero_image", "about_short")}),
        ("Statistics", {"fields": ("years_experience", "patients_treated", "success_rate")}),
    )


@admin.register(DoctorProfile)
class DoctorProfileAdmin(SingletonAdmin):
    list_display = ("name", "title", "years_experience")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "duration_minutes", "price", "is_featured", "order")
    list_editable = ("is_featured", "order")
    list_filter = ("is_featured",)
    search_fields = ("name", "short_description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("patient_name", "rating", "service", "is_published", "created_at")
    list_filter = ("is_published", "rating")
    list_editable = ("is_published",)
    search_fields = ("patient_name", "quote")


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "order", "is_published")
    list_editable = ("order", "is_published")


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published_at", "is_published")
    list_filter = ("is_published", "author")
    list_editable = ("is_published",)
    search_fields = ("title", "excerpt", "content")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "order", "is_published", "preview")
    list_editable = ("order", "is_published")
    list_filter = ("category", "is_published")

    @admin.display(description="Preview")
    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:38px;border-radius:6px;" />', obj.image.url)
        return "—"


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "service", "date", "time", "status", "created_at")
    list_filter = ("status", "date", "service")
    search_fields = ("name", "phone", "email")
    date_hierarchy = "date"
    readonly_fields = ("created_at", "updated_at")
    actions = ("mark_confirmed", "mark_completed", "mark_cancelled")

    @admin.action(description="Mark selected as confirmed")
    def mark_confirmed(self, request, queryset):
        queryset.update(status=Appointment.STATUS_CONFIRMED)

    @admin.action(description="Mark selected as completed")
    def mark_completed(self, request, queryset):
        queryset.update(status=Appointment.STATUS_COMPLETED)

    @admin.action(description="Mark selected as cancelled")
    def mark_cancelled(self, request, queryset):
        queryset.update(status=Appointment.STATUS_CANCELLED)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "is_read", "created_at")
    list_filter = ("is_read",)
    list_editable = ("is_read",)
    search_fields = ("name", "email", "message")
    readonly_fields = ("created_at",)
