from datetime import date

from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render
from django.views.generic import CreateView, FormView, ListView, UpdateView

from .forms import EBookForm, EbookSearchForm, RegisterForm
from .models import EBook

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


class CreateEBook(LoginRequiredMixin, CreateView):
    form_class = EBookForm
    template_name = "manage_ebooks/create_ebook.html"
    success_url = "/"
    login_url = "/login/"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user

        return kwargs


class EditEBook(LoginRequiredMixin, UpdateView):
    model = EBook
    form_class = EBookForm
    template_name = "manage_ebooks/edit_ebook.html"
    success_url = "/"
    login_url = "/login/"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user

        return kwargs


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

            if title:
                qs = qs.filter(title__icontains=title)

            if tag:
                qs = qs.filter(tags__name__in=tag.split())

            if description:
                qs = qs.filter(description__icontains=description)

            if author:
                qs = qs.filter(author=author)

        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["today"] = date.today()

        form = EbookSearchForm(self.request.GET)
        context["form"] = form

        return context
