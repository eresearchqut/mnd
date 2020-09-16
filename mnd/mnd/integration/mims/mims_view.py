import logging


from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .mims_service import MIMSService
from .mims_cache import (
    CMIInfo, ProductInfo, get_cache, get_cmi_cache,
    search_cache, update_cache, update_cache_entry,
    update_cmi_cache
)

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
        cached = get_cache(product)
        if cached and cached.mims:
            return JsonResponse(status=200, data=cached._asdict())
        product_details = MIMSService().get_product_details(product)
        if product_details:
            mims = ", ".join(product_details['mimsClasses'])
            name = product_details.get('productName', '')
            product_info = ProductInfo(product, name, mims, '')
            resp = update_cache_entry(product_info)._asdict()

    return JsonResponse(status=200, data=resp)


def _handle_cmi_details(mims_service, product_id, product_name, cmi_id):
    cmi_details = mims_service.get_cmi_details(cmi_id)
    if cmi_details:
        products = [p for p in cmi_details.get('products', [])]
        document_link = [
            d['cmiDocument'] for d in cmi_details['cmiDocuments'] if d['cmiFormat'] in ('pdf', 'reducedpdf')
        ]
        if document_link and document_link[0]:
            for p in products:
                update_cmi_cache(CMIInfo(p['productId'], p['productName'], cmi_id, document_link[0], True))
            cmi_info = update_cmi_cache(CMIInfo(product_id, '', cmi_id, document_link[0], True))
            return cmi_info
        return update_cmi_cache(CMIInfo(product_id, product_name, cmi_id, '', False))


@require_GET
def cmi_details(request):
    product = request.GET.get("product", "")
    resp = {}
    if product:
        cached = get_cmi_cache(product)
        if cached and (cached.link or not cached.has_link):
            return JsonResponse(status=200, data=cached._asdict())

        resp = {}
        ms = MIMSService()
        product_details = ms.get_product_details(product)
        if product_details:
            product_name = product_details.get('productName')
            cmis = product_details.get('cmis', [])
            cmi_id = cmis[0]['cmiId'] if cmis else None
            if cached:
                cmi_info = CMIInfo(cached.product_id, cached.name, cmi_id, '', cmi_id is not None)
            else:
                cmi_info = CMIInfo(product, product_name, cmi_id, '', cmi_id is not None)
            cmi_info = update_cmi_cache(cmi_info)
            if cmi_info.cmi_id:
                updated = _handle_cmi_details(ms, product, product_name, cmi_info.cmi_id)
                if updated:
                    resp = updated._asdict()
            else:
                resp = cmi_info._asdict()

    return JsonResponse(status=200, data=resp)
