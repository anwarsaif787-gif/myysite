from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class SiteSettings(SingletonModel):
    clinic_name = models.CharField(
        max_length=120, default="Sami Physiotherapy & Rehab. Center"
    )
    doctor_name = models.CharField(max_length=120, default="Dr. Osama Sami")
    tagline = models.CharField(
        max_length=200, default="Movement restored. Life reclaimed."
    )
    phone = models.CharField(max_length=40, blank=True, default="+91 98520 60649")
    whatsapp = models.CharField(max_length=40, blank=True, default="919852060649")
    email = models.EmailField(blank=True, default="samiphysio1992@gmail.com")
    address = models.CharField(
        max_length=255,
        blank=True,
        default="Gaushala Rd, Doctors Colony, Siwan, Bihar 841227, India",
    )
    location_short = models.CharField(max_length=120, blank=True, default="Siwan, Bihar")
    directions_url = models.URLField(
        blank=True, default="https://maps.app.goo.gl/9h8JbgSBrXt8K8qC7?g_st=aw"
    )
    map_embed_url = models.URLField(
        blank=True,
        default="https://www.google.com/maps?q=Gaushala+Rd,+Doctors+Colony,+Siwan,+Bihar+841227&z=16&output=embed",
    )
    working_hours = models.CharField(
        max_length=200,
        blank=True,
        default="Mon – Thu & Sat – Sun: 9:00 AM – 5:00 PM",
    )
    facebook = models.URLField(blank=True)
    instagram = models.URLField(
        blank=True, default="https://www.instagram.com/osamasami2511/"
    )
    linkedin = models.URLField(blank=True)
    youtube = models.URLField(blank=True)

    hero_heading = models.CharField(
        max_length=160, default="Expert Physiotherapy for a Stronger, Pain-Free Life"
    )
    hero_subheading = models.TextField(
        blank=True,
        default=(
            "Personalised, evidence-based rehabilitation guided by over a decade "
            "of clinical experience — so you can move with confidence again."
        ),
    )
    hero_image = models.ImageField(upload_to="site/", blank=True)
    about_short = models.TextField(
        blank=True,
        default=(
            "For more than ten years, Dr. Osama Sami has helped patients recover "
            "from injury, manage chronic pain, and return to the activities they love."
        ),
    )
    years_experience = models.PositiveIntegerField(default=10)
    patients_treated = models.PositiveIntegerField(default=4500)
    success_rate = models.PositiveIntegerField(default=98)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.clinic_name


class DoctorProfile(SingletonModel):
    name = models.CharField(max_length=120, default="Dr. Osama Sami")
    title = models.CharField(max_length=120, default="Consultant Physiotherapist")
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="doctor/", blank=True)
    years_experience = models.PositiveIntegerField(default=10)
    credentials = models.TextField(
        blank=True,
        help_text="One credential per line.",
        default=(
            "Bachelor of Physiotherapy (BPT)\n"
            "Master of Physiotherapy (MPT)\n"
            "Consultant Physiotherapist"
        ),
    )
    specialties = models.TextField(
        blank=True,
        help_text="One specialty per line.",
        default=(
            "Spine & posture rehabilitation\n"
            "Sports injury recovery\n"
            "Post-surgical rehabilitation\n"
            "Chronic pain management\n"
            "Manual therapy & dry needling"
        ),
    )

    class Meta:
        verbose_name = "Doctor Profile"
        verbose_name_plural = "Doctor Profile"

    def __str__(self):
        return self.name

    @property
    def credential_list(self):
        return [line.strip() for line in self.credentials.splitlines() if line.strip()]

    @property
    def specialty_list(self):
        return [line.strip() for line in self.specialties.splitlines() if line.strip()]


class Service(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    short_description = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=40,
        default="spine",
        help_text="spine, knee, sports, rehab, massage, posture, neuro, pain",
    )
    image = models.ImageField(upload_to="services/", blank=True)
    duration_minutes = models.PositiveIntegerField(default=45)
    price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("clinic:service_detail", args=[self.slug])


class Testimonial(models.Model):
    patient_name = models.CharField(max_length=120)
    patient_photo = models.ImageField(upload_to="testimonials/", blank=True)
    rating = models.PositiveSmallIntegerField(default=5)
    quote = models.TextField()
    service = models.ForeignKey(
        Service, on_delete=models.SET_NULL, null=True, blank=True, related_name="testimonials"
    )
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.patient_name} ({self.rating}/5)"

    @property
    def stars(self):
        return range(self.rating)


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    cover_image = models.ImageField(upload_to="blog/", blank=True)
    author = models.CharField(max_length=120, default="Dr. Osama Sami")
    tags = models.CharField(max_length=200, blank=True, help_text="Comma separated")
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("clinic:blog_detail", args=[self.slug])

    @property
    def tag_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]


class GalleryImage(models.Model):
    title = models.CharField(max_length=140, blank=True)
    image = models.ImageField(upload_to="gallery/")
    category = models.CharField(max_length=80, blank=True, default="Clinic")
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title or f"Gallery image {self.pk}"


class Appointment(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    service = models.ForeignKey(
        Service, on_delete=models.SET_NULL, null=True, related_name="appointments"
    )
    date = models.DateField()
    time = models.TimeField()
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date", "time"]
        constraints = [
            models.UniqueConstraint(
                fields=["date", "time"],
                condition=Q(status__in=["pending", "confirmed"]),
                name="unique_active_slot",
            )
        ]

    def __str__(self):
        return f"{self.name} — {self.date} {self.time:%H:%M}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    subject = models.CharField(max_length=160, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.subject or 'Message'}"
