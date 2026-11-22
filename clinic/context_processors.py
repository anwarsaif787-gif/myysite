from .models import DoctorProfile, SiteSettings


def site_settings(request):
    return {
        "site": SiteSettings.load(),
        "doctor": DoctorProfile.load(),
    }
