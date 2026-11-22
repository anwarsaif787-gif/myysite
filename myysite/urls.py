from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from clinic.sitemaps import BlogSitemap, ServiceSitemap, StaticViewSitemap

admin.site.site_header = "Osama Sami Physiotherapy"
admin.site.site_title = "Osama Sami Physiotherapy Admin"
admin.site.index_title = "Clinic Management"

sitemaps = {
    "static": StaticViewSitemap,
    "services": ServiceSitemap,
    "blog": BlogSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("", include("clinic.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "clinic.views.custom_404"
handler500 = "clinic.views.custom_500"
