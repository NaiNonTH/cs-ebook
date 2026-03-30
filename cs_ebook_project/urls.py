from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.admin.views.decorators import staff_member_required # Import for staff check

from ebooks import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("ebooks.urls")),
    path("market/", include("market.urls")),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)