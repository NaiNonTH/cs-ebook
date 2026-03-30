from datetime import date

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import EBook


class CreateEBookForm(forms.ModelForm):
    class Meta:
        model = EBook
        fields = [
            "title",
            "category",
            "description",
            "cover",
            "sample",
            "token",
            "publish_date",
            "tags",
        ]
        widgets = {
            "publish_date": forms.DateInput(
                attrs={"type": "date"},
            )
        }

    def __init__(self, *args, user=None, **kwargs):
        self.page_images = kwargs.pop('page_images', None)
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        publish_date = cleaned_data.get("publish_date")
    
        if publish_date:
            cleaned_data["post_status"] = "P" if publish_date <= date.today() else "U"
    
        uploaded_files = self.page_images.getlist('images') if self.page_images else []
    
        # validate PNG only
        non_png = [
            f.name for f in uploaded_files
            if not f.name.lower().endswith('.png') or f.content_type not in {'image/png'}
        ]
        if non_png:
            raise forms.ValidationError(
                f"ไฟล์ต่อไปนี้ไม่ใช่ .png: {', '.join(non_png)} กรุณาอัพโหลดเฉพาะไฟล์ .png เท่านั้น"
            )
    
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.post_status = self.cleaned_data["post_status"]
        instance.author = self.user
    
        # derive page count from uploaded images
        uploaded_files = self.page_images.getlist('images') if self.page_images else []
        instance.page_count = len(uploaded_files)
    
        if commit:
            instance.save()
            self.save_m2m()
    
        return instance
    

class EditEBookForm(forms.ModelForm):
    class Meta:
        model = EBook
        fields = [
            "title",
            "category",
            "description",
            "cover",
            "token",
            "publish_date",
            "tags",
        ]
        widgets = {
            "publish_date": forms.DateInput(
                attrs={"type": "date"},
            )
        }

    def clean(self):
        cleaned_data = super().clean()
        publish_date = cleaned_data.get("publish_date")

        cleaned_data["post_status"] = "P" if publish_date <= date.today() else "U"

        return cleaned_data
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.post_status = self.cleaned_data["post_status"]

        if commit:
            instance.save()
            self.save_m2m()

        return instance


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )


class EbookSearchForm(forms.Form):
    User = get_user_model()
    title = forms.CharField(required=False, label="Title")
    tag = forms.CharField(required=False, label="Tag")
    description = forms.CharField(required=False, label="Description")
    category = forms.ChoiceField(
        required=False,
        choices=[("", "---")] + EBook._meta.get_field("category").choices,
        initial="",
    )
    author = forms.ModelChoiceField(
        queryset=User.objects.all(), required=False, empty_label="All authors"
    )
