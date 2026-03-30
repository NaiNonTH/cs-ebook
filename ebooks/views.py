import os
import re
from datetime import date

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import CreateView, DetailView, FormView, ListView, UpdateView

from .forms import CreateEBookForm, EditEBookForm, EbookSearchForm, RegisterForm
from .models import EBook

from django.shortcuts import get_object_or_404
from django.views import View

from django.core.exceptions import PermissionDenied

# Create your views here.


class Login(FormView):
    template_name = "auth/login.html"
    form_class = AuthenticationForm
    success_url = "/"

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)


class Register(CreateView):
    template_name = "auth/register.html"
    form_class = RegisterForm
    success_url = "/login/"
    
    
class ManageEBook(LoginRequiredMixin, ListView):
    model = EBook
    template_name = "manage_ebooks/manage_ebook.html"
    login_url = "/login/"
    
    def get_queryset(self):
        return EBook.objects.filter(author__username=self.request.user.username)


class CreateEBook(LoginRequiredMixin, CreateView):
    form_class = CreateEBookForm
    template_name = "manage_ebooks/create_ebook.html"
    success_url = "/manage"
    login_url = "/login/"
    
    def natural_sort_key(self, filename):
        return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', filename)]

    def form_valid(self, form):
        # save the Ebook instance first
        response = super().form_valid(form)

        # then handle page image uploads
        files = self.request.FILES.getlist('images')

        save_dir = os.path.join(settings.MEDIA_ROOT, f'books/{self.object.pk}')
        
        os.makedirs(save_dir, exist_ok=True)

        for index, f in enumerate(files, start=1):
            ext = os.path.splitext(f.name)[1]
            new_name = f"page_{index}{ext}"
            file_path = os.path.join(save_dir, new_name)
            with open(file_path, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)

        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs['page_images'] = self.request.FILES

        return kwargs


class EditEBook(LoginRequiredMixin, UpdateView):
    model = EBook
    form_class = EditEBookForm
    template_name = "manage_ebooks/edit_ebook.html"
    success_url = "/manage"
    login_url = "/login/"


class ListEBook(LoginRequiredMixin, ListView):
    model = EBook
    template_name = "manage_ebooks/list_ebook.html"
    login_url = "/login/"

    def get_queryset(self):
        self.form = EbookSearchForm(self.request.GET)

        qs = EBook.objects.all()

        if not self.request.GET:
            return qs

        if self.form.is_valid():
            title = self.form.cleaned_data.get("title")
            tag = self.form.cleaned_data.get("tag")
            description = self.form.cleaned_data.get("description")
            author = self.form.cleaned_data.get("author")
            category = self.form.cleaned_data.get("category")

            if title:
                qs = qs.filter(title__icontains=title)

            if tag:
                qs = qs.filter(tags__name__in=tag.split())

            if description:
                qs = qs.filter(description__icontains=description)

            if author:
                qs = qs.filter(author=author)

            if category:
                qs = qs.filter(category__exact=category)

        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["today"] = date.today()

        form = EbookSearchForm(self.request.GET)
        context["form"] = form
        return context


def logout_view(request):
    logout(request)
    return redirect(reverse("login"))

class PreviewEBook(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, pk):
        ebook = get_object_or_404(EBook, pk=pk)

        if ebook.author != request.user:
            return render(request, "403.html")

        context = {
            'ebook': ebook,
            'is_preview': True
        }
        return render(request, 'reader/read_ebook.html', context)

class EBookDetailView(LoginRequiredMixin, DetailView):
    model = EBook
    template_name = 'ebooks/ebook_detail.html'
    context_object_name = 'ebook'
    login_url = "/login/"

    def get_object(self):
        ebook = super().get_object()

        if ebook.author != self.request.user:
            raise PermissionDenied

        return ebook

class ReadEBook(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, pk):
        ebook = get_object_or_404(EBook, pk=pk)

        if ebook.author != request.user:
            return render(request, "403.html")

        folder_path = os.path.join(settings.MEDIA_ROOT, f'books/{ebook.id}')

        if not os.path.exists(folder_path):
            return render(request, 'reader/read_ebook.html', {
                'ebook': ebook,
                'error': 'ไม่พบไฟล์หนังสือ'
            })

        pages = sorted([
            f for f in os.listdir(folder_path)
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ])

        total_pages = len(pages)

        if total_pages == 0:
            return render(request, 'reader/read_ebook.html', {
                'ebook': ebook,
                'error': 'ยังไม่มีหน้าหนังสือ'
            })

        page_str = request.GET.get('page')
        try:
            page = int(page_str) if page_str else 1
        except ValueError:
            page = 1

        if page < 1:
            page = 1
        if page > total_pages:
            page = total_pages

        current_image = f'/media/books/{ebook.id}/{pages[page-1]}'

        return render(request, 'reader/read_ebook.html', {
            'ebook': ebook,
            'page': page,
            'total_pages': total_pages,
            'current_image': current_image,
        })