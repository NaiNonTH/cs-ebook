import os
import re
from datetime import date

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import CreateView, DetailView, FormView, ListView, UpdateView

from .forms import CreateEBookForm, EditEBookForm, EbookSearchForm, RegisterForm
from .models import EBook, LogRead

from django.shortcuts import get_object_or_404
from django.views import View

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

        form = EbookSearchForm(self.request.GET)
        context["form"] = form
        
        return context


def logout_view(request):
    logout(request)
    return redirect(reverse("login"))


class ReadEBook(View):
    def get(self, request, pk):
        ebook = get_object_or_404(EBook, pk=pk)
        
        if ebook.post_status != 'P':
            return Http404()

        page_str = request.GET.get('page', '1')

        try:
            page = int(page_str)
        except (ValueError, TypeError):
            page = 1

        if page < 1:
            page = 1
        if page > ebook.page_count:
            page = ebook.page_count

        if request.user.is_authenticated:
            LogRead.objects.get_or_create(
                user=request.user,
                ebook=ebook,
                page_number=page,
            )

        context = {
            'ebook': ebook,
            'page': page,
            'total_pages': ebook.page_count,
            'is_preview': False
        }
        
        return render(request, 'reader/read_ebook.html', context)
    
from django.views.generic import DetailView
from .models import EBook


class EBookDetailView(DetailView):
    model = EBook
    template_name = 'ebooks/ebook_detail.html'
    context_object_name = 'ebook'


class ReadingDashboard(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        ebook_ids = (
            LogRead.objects
            .filter(user=request.user)
            .values_list('ebook', flat=True)
            .distinct()
        )
        ebooks = EBook.objects.filter(pk__in=ebook_ids)

        books_data = []
        for ebook in ebooks:
            pages_read = LogRead.objects.filter(user=request.user, ebook=ebook).count()
            percent = min(round((pages_read / ebook.page_count) * 100), 100) if ebook.page_count else 0
            books_data.append({
                'ebook': ebook,
                'pages_read': pages_read,
                'percent': percent,
            })

        return render(request, 'ebooks/reading_dashboard.html', {'books_data': books_data})