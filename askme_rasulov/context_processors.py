from django.core.cache import cache
from django.conf import settings


def get_base_context(request):
    best_members = cache.get('best_members')
    popular_tags = cache.get('popular_tags')

    return {
        'best_members': best_members,
        'popular_tags': popular_tags,
    }
