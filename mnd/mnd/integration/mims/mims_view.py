from collections import namedtuple
import logging


from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .mims_service import MIMSService

logger = logging.getLogger(__name__)


ProductInfo = namedtuple('ProductInfo', 'id name mims activeIngredient')

productCache = {}


@require_GET
def product_search(request):

    def active_ingredient(result):
        return ", ".join(result.split("+"))

    product = request.GET.get("term", "")
    if product and product.strip() != '' and len(product) >= 4:
        result = MIMSService().search_product(product)
        if result:
            formatted = [{
                'id': r['productId'],
                'value': r['productName'],
                'activeIngredient': active_ingredient(r['activeIngredient'])
            } for r in result]
            productCache.update({
                f['id']: ProductInfo(f['id'], f['value'], '', f['activeIngredient'])
                for f in formatted
            })
            return JsonResponse(status=200, data=formatted, safe=False)
    return JsonResponse(status=200, data=[], safe=False)


@require_GET
def product_details(request):
    product = request.GET.get("product", "")
    if product:
        ms = MIMSService()
        resp = {}
        cached = productCache.get(product, {})
        if not cached or not cached.mims:
            product_details = ms.get_product_details(product)
            if product_details:
                resp['mims'] = ", ".join(product_details['mimsClasses'])
                resp['productName'] = product_details.get('productName', '')
                resp['activeIngredient'] = cached.activeIngredient if cached else ''
                if not cached:
                    productCache[product] = ProductInfo(product, resp['productName'], resp['mims'], '')
                else:
                    productCache[product] = ProductInfo(cached.id, cached.name, resp['mims'], cached.activeIngredient)
        else:
            resp['mims'] = cached.mims
            resp['productName'] = cached.name
            resp['activeIngredient'] = cached.activeIngredient

        return JsonResponse(status=200, data=resp)
    return JsonResponse(status=200, data={})
