from django.core.management.base import BaseCommand
from ebooks.models import EBook, LogRead
from market.models import MarketShare
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Clears ALL existing dummy data from the database'

    def handle(self, *args, **kwargs):
        self.stdout.write("Clearing old data...")

        # Delete all dummy users (which cascades to delete their LogReads and created EBooks)
        User.objects.filter(username__startswith='dummy_user_').delete()
        
        # Just to be safe, delete any MarketShare calculations
        MarketShare.objects.all().delete()
        
        # If there are any EBooks specifically titled "Dummy Ebook", delete those too
        EBook.objects.filter(title__startswith='Dummy Ebook').delete()

        self.stdout.write(self.style.SUCCESS('Successfully cleared all dummy data!'))
