from django.urls import path
from . import views

urlpatterns = [
    path('ebook/<int:pk>/preview/', views.PreviewEBook.as_view(), name='preview_ebook'),
    path('ebook/<int:pk>/read/', views.ReadEBook.as_view(), name='read_ebook'),
]