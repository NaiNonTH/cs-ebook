from datetime import date

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import EBook


class EBookForm(forms.ModelForm):
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
            "page_count",
            "tags",
        ]
        widgets = {
            "publish_date": forms.DateInput(
                attrs={"type": "date"},
            )
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()
        publish_date = cleaned_data.get("publish_date")

        cleaned_data["post_status"] = "P" if publish_date <= date.today() else "U"

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.post_status = self.cleaned_data["post_status"]
        instance.author = self.user

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
