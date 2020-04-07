from django.core.management.base import BaseCommand
from app.models import User
from faker import Faker


class Command(BaseCommand):
    def handle(self, counts, *args, **options):
        fake = Faker()
        names = set([fake.name() for _ in range(counts)])
        users = [User(username=name) for name in names]
        User.objects.bulk_create(users)
