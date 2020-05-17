from .generate_question import Command as gen_quest
from .generate_user import Command as gen_user
from .generate_tags import Command as gen_tags
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('start generate users')
        gen_user().handle(10000, *args, **options)
        print('finish generate users, start generate tags')
        gen_tags().handle(10000, *args, **options)
        print('finish generate tags, start generate question')
        gen_quest().handle(100000, 10, *args, **options)
        print('finish generate question')
