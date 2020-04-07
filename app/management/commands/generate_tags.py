from django.core.management.base import BaseCommand
from app.models import Tag
from faker import Faker


class Command(BaseCommand):
    def handle(self, counts, *args, **options):
        fake = Faker()
        titles = set([fake.word() for _ in range(counts)])
        tags = [Tag(title=title) for title in titles]
        Tag.objects.bulk_create(tags)
