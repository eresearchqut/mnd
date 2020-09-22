from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.views.decorators.http import require_GET

from .mims_service import (
    fetch_pdf, mims_cmi_details, mims_product_details, mims_product_search
)


@require_GET
def product_search(request):
    product = request.GET.get("term", "")
    result = [r._asdict() for r in mims_product_search(product)]
    return JsonResponse(status=200, data=result, safe=False)


@require_GET
def product_details(request):
    product = request.GET.get("product", "")
    return JsonResponse(status=200, data=mims_product_details(product))


@require_GET
def cmi_details(request):
    product = request.GET.get("product", "")
    return JsonResponse(status=200, data=mims_cmi_details(product))


@require_GET
def pdf_proxy(request):
    cmi = request.GET.get("cmi", "")
    resp = fetch_pdf(cmi)
    if not resp:
        return HttpResponseNotFound()
    return HttpResponse(
        content=resp.content,
        status=resp.status_code,
        content_type=resp.headers['Content-Type']
    )
