from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from app.models import *

CACHE_TIME = 10


class Command(BaseCommand):
    def handle(self, *args, **options):
        popular_tags = Tag.objects.popular()
        cache.set('popular_tags', popular_tags, CACHE_TIME)

        best_members = Profile.objects.best()
        cache.set('best_members', best_members, CACHE_TIME)
