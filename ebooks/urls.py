from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.Login.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.Register.as_view(), name="register"),
    path("manage/", views.ManageEBook.as_view(), name="manage_ebook"),
    path("manage/create/", views.CreateEBook.as_view(), name="create_ebook"),
    path("manage/edit/<int:pk>/", views.EditEBook.as_view(), name="edit_ebook"),
    path('<int:pk>/', views.EBookDetailView.as_view(), name='ebook_detail'),
    path('<int:pk>/read/', views.ReadEBook.as_view(), name='read_ebook'),
]