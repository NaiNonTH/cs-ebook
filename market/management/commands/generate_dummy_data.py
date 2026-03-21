import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ebooks.models import EBook, LogRead
from market.models import MarketShare

class Command(BaseCommand):
    help = 'Generates dummy data for EBook, LogRead, and MarketShare'

    def handle(self, *args, **kwargs):
        self.stdout.write("Generating dummy data...")

        # Create dummy users
        users = []
        for i in range(5):
            user, created = User.objects.get_or_create(username=f'dummy_user_{i}', defaults={'email': f'dummy{i}@example.com'})
            if created:
                user.set_password('password123')
                user.save()
            users.append(user)

        author = users[0]

        # Create dummy ebooks
        ebooks = []
        categories = ['COMP', 'DATA', 'CENG']
        for i in range(5):
            ebook, created = EBook.objects.get_or_create(
                title=f'Dummy Ebook {i}',
                defaults={
                    'category': random.choice(categories),
                    'author': author,
                    'description': f'Description for dummy ebook {i}',
                    'token': random.randint(10, 100),
                    'publish_date': date.today() - timedelta(days=random.randint(30, 365)),
                    'page_count': random.randint(50, 500),
                    'post_status': 'P'
                }
            )
            ebooks.append(ebook)
            if created:
                 ebook.tags.add(f'tag{i}', 'dummy')

        # Create dummy log reads
        for _ in range(20):
             LogRead.objects.create(
                 user=random.choice(users),
                 ebook=random.choice(ebooks),
                 page_number=random.randint(1, 50)
             )

        # Create dummy MarketShare
        months = [date(date.today().year, m, 1) for m in range(1, 13)]
        for ebook in ebooks:
            for month in random.sample(months, k=3): # Pick 3 random months for each book
                MarketShare.objects.get_or_create(
                    ebook=ebook,
                    month=month,
                    defaults={'uread': random.randint(10, 500)}
                )

        self.stdout.write(self.style.SUCCESS('Successfully generated dummy data!'))
