from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.admin.views.decorators import staff_member_required # Import for staff check

from ebooks import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", views.Login.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.Register.as_view(), name="register"),
    path("manage/", staff_member_required(views.ManageEBook.as_view()), name="manage_ebook"),
    path("manage/create/", staff_member_required(views.CreateEBook.as_view()), name="create_ebook"),
    path("manage/edit/<int:pk>/", staff_member_required(views.EditEBook.as_view()), name="edit_ebook"),
    path('ebook/<int:pk>/detail/', views.EBookDetailView.as_view(), name='ebook_detail'),
    path('ebook/<int:pk>/preview/', views.PreviewEBook.as_view(), name='preview_ebook'),
    path('ebook/<int:pk>/read/', views.ReadEBook.as_view(), name='read_ebook'),
    path("market/", include("market.urls")),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)