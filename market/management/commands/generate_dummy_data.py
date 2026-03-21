import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ebooks.models import EBook, LogRead

class Command(BaseCommand):
    help = 'Generates dummy data for EBook and mixed LogRead (sequential and random)'

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
                    'page_count': random.randint(50, 100), # keep page count reasonable
                    'post_status': 'P'
                }
            )
            ebooks.append(ebook)
            if created:
                 ebook.tags.add(f'tag{i}', 'dummy')

        # Clear old dummy logs to prevent clutter
        LogRead.objects.filter(user__in=users).delete()

        # Reading styles
        # 1. "Good Reader": Reads sequentially and usually finishes (Passes easily)
        # 2. "Quitter": Reads sequentially but stops early (Fails 50% rule)
        # 3. "Jumper": Reads randomly all over the place (Passes 50% rule, Fails 40% sequence rule)
        # 4. "Your Example Jumper": Specifically inject the pattern you asked for

        reading_styles = ["good", "quitter", "jumper", "example_jumper"]

        for user in users[1:]: # Users other than the author read the books
            for ebook in random.sample(ebooks, k=3): # Each user picks 3 random books to read
                style = random.choice(reading_styles)
                pages_to_read = []

                if style == "good":
                    percent_read = random.choice([0.6, 0.8, 1.0])
                    num_pages = int(ebook.page_count * percent_read)
                    pages_to_read = list(range(1, num_pages + 1))
                
                elif style == "quitter":
                    percent_read = random.choice([0.1, 0.2, 0.3])
                    num_pages = int(ebook.page_count * percent_read)
                    pages_to_read = list(range(1, num_pages + 1))
                
                elif style == "jumper":
                    # They read a lot of pages (e.g., 60%), but completely randomly, huge gaps
                    num_pages = int(ebook.page_count * 0.6)
                    all_pages = list(range(1, ebook.page_count + 1))
                    pages_to_read = random.sample(all_pages, k=num_pages)
                
                elif style == "example_jumper":
                    # Based on your example: 1, 7, 8, 9, 10 then 2, 19, 3, 7, 5, 4
                    # This guarantees bad sequence but enough volume if the book is small
                    # We will ensure they read ~60% of the book randomly to fail the 40% continuous rule
                    base_pattern = [1, 7, 8, 9, 10, 2, 19, 3, 7, 5, 4]
                    extra_random_pages = random.sample(range(20, ebook.page_count + 1), k=int(ebook.page_count * 0.5))
                    pages_to_read = base_pattern + extra_random_pages

                for page_num in pages_to_read:
                    # Ignore invalid pages just in case
                    if page_num <= ebook.page_count:
                        LogRead.objects.create(
                            user=user,
                            ebook=ebook,
                            page_number=page_num
                        )

        self.stdout.write(self.style.SUCCESS('Successfully generated mixed dummy data (passed and failed scenarios)!'))
