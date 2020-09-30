from django.http import JsonResponse
from rdrf.models.definition.models import Registry

from ..integration.mims.mims_cache import evict_expired_entries


def health_check(request):
    evict_expired_entries()
    return JsonResponse({
        'success': True,
        'hosted_registries_count': Registry.objects.count(),
    })
