from django import forms

from .models import EBook

from datetime import date

class EBookForm(forms.ModelForm):
	class Meta:
		model = EBook
		fields = ['title', 'category', 'description', 'cover', 'sample', 'token', 'publish_date', 'page_count', 'tags']
		widgets = {
			'publish_date': forms.DateInput(
				attrs={'type': 'date'},
			)
		}
  
	def __init__(self, *args, user=None, **kwargs):
		super().__init__(*args, **kwargs)
		self.user = user
	
	def clean(self):
		cleaned_data = super().clean()
		publish_date = cleaned_data.get('publish_date')

		cleaned_data['post_status'] = 'P' if publish_date <= date.today() else 'U'
  
		return cleaned_data

	def save(self, commit=True):
		instance = super().save(commit=False)
		instance.post_status = self.cleaned_data['post_status']
		instance.author = self.user

		if commit:
			instance.save()
			self.save_m2m()
   
		return instance