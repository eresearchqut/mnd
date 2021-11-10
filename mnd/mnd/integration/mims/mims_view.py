from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET

from .mims_service import (
    fetch_pdf, mims_product_cmis, mims_product_details, mims_product_search,
)


@require_GET
def product_search(request):
    product = request.GET.get("term", "")
    products = [p._asdict() for p in mims_product_search(product)]
    return JsonResponse(status=200, data=products, safe=False)


@require_GET
def product_details(request):
    product = request.GET.get("product", "")
    product_info = mims_product_details(product)
    response = product_info._asdict() if product_info else {}
    return JsonResponse(status=200, data=response)


@require_GET
def cmi_details(request):
    product = request.GET.get("product", "")
    product_name, cmis = mims_product_cmis(product)
    response = {"productName": product_name, "details": [c._asdict() for c in cmis]}
    return JsonResponse(status=200, data=response)


@require_GET
def pdf_proxy(request):
    cmi = request.GET.get("cmi", "")
    resp = fetch_pdf(cmi)
    if not resp:
        return HttpResponseNotFound(_("Consumer medicine information PDF not found"))
    return HttpResponse(
        content=resp.content,
        status=resp.status_code,
        content_type=resp.headers['Content-Type']
    )
