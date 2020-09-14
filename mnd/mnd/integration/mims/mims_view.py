import logging


from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .mims_service import MIMSService
from .mims_cache import ProductInfo, get_cache, search_cache, update_cache, update_cache_entry

logger = logging.getLogger(__name__)


@require_GET
def product_search(request):

    def active_ingredient(result):
        return ", ".join(result.split("+"))

    product = request.GET.get("term", "")
    if product and product.strip() != '' and len(product) >= 4:
        cached = search_cache(product)
        if cached:
            formatted = [{
                'id': r.id,
                'value': r.name,
                'activeIngredient': r.activeIngredient
            } for r in cached]
            return JsonResponse(status=200, data=formatted, safe=False)

        result = MIMSService().search_product(product)
        if result:
            formatted = [{
                'id': r['productId'],
                'value': r['productName'],
                'activeIngredient': active_ingredient(r['activeIngredient'])
            } for r in result]
            update_cache(product, formatted)
            return JsonResponse(status=200, data=formatted, safe=False)
    return JsonResponse(status=200, data=[], safe=False)


@require_GET
def product_details(request):
    product = request.GET.get("product", "")
    resp = {}
    if product:
        ms = MIMSService()
        cached = get_cache(product)
        if cached and cached.mims:
            return JsonResponse(status=200, data=cached._asdict())

        product_details = ms.get_product_details(product)
        if product_details:
            mims = ", ".join(product_details['mimsClasses'])
            name = product_details.get('productName', '')
            product_info = ProductInfo(product, name, mims, '')
            resp = update_cache_entry(product_info)._asdict()

    return JsonResponse(status=200, data=resp)
