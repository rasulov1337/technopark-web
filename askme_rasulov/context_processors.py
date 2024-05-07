from app.models import *


def get_base_context(request):
    return {
        'best_members': Profile.objects.best(),
        'popular_tags': Tag.objects.popular(),
    }