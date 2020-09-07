import logging


from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .mims_service import MIMSService

logger = logging.getLogger(__name__)


@require_GET
def brand_seach(request):
    brand = request.GET.get("term", "")
    if brand and brand.strip() != '' and len(brand) >= 4:
        result = MIMSService().search_brand(brand)
        formatted = [{
            'id': r['brandId'],
            'value': r['brandName'],
            'label': r['brandName']
        } for r in result]
        return JsonResponse(status=200, data=formatted, safe=False)
    return JsonResponse(status=200, data=[], safe=False)
