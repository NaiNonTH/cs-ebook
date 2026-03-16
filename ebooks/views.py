from django.shortcuts import render
from django.views.generic import FormView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth.models import User

from .forms import EBookForm, RegisterForm
from .models import EBook

# Create your views here.

class Login(FormView):
	template_name = 'auth/login.html'
	form_class = AuthenticationForm
	success_url = '/'

	def form_valid(self, form):
		login(self.request, form.get_user())
		return super().form_valid(form)

class Register(CreateView):
	template_name = 'auth/register.html'
	form_class = RegisterForm
	success_url = '/login/'

class CreateEBook(LoginRequiredMixin, CreateView):
	form_class = EBookForm
	template_name = 'manage_ebooks/create_ebook.html'
	success_url = '/'
	login_url = '/login/'

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs['user'] = self.request.user
  
		return kwargs

class EditEBook(LoginRequiredMixin, UpdateView):
	model = EBook
	form_class = EBookForm
	template_name = 'manage_ebooks/edit_ebook.html'
	success_url = '/'
	login_url = '/login/'

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs['user'] = self.request.user
  
		return kwargs