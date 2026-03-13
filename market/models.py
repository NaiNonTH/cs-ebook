from django.db import models

from ebooks.models import EBook

# Create your models here.

class MarketShare(models.Model):
	ebook = models.ForeignKey(EBook, on_delete=models.CASCADE)
	month = models.DateField()
	uread = models.IntegerField()

	class Meta:
		unique_together = ('ebook', 'month')