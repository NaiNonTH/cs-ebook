from django.contrib import admin
from .models import EBook, LogRead

# Register your models here.

from .models import EBook

admin.site.register(EBook)
admin.site.register(LogRead)
