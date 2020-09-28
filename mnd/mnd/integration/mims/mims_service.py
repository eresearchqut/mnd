from collections import namedtuple
import logging
import requests
import uuid

from django.shortcuts import reverse

from .mims_api import MIMSApi
from .mims_cache import (
    CMIInfo, ProductInfo, get_product, get_cmi_by_product,
    get_cmi_info, search_cache, update_cache,
    update_cache_entry, update_cmi_cache
)

ProductSearchResult = namedtuple('ProductSearchResult', 'id value activeIngredient')

logger = logging.getLogger(__name__)

api = MIMSApi()


def _is_valid_uuid(input_str):
    try:
        uuid.UUID(input_str)
    except Exception:
        return False
    return True


def mims_product_search(product, page):

    def active_ingredient(result):
        return ", ".join(result.split(" + "))

    has_next = False
    if product and product.strip() != '' and len(product) >= 4:
        cached = search_cache(product)
        if cached:
            return [ProductSearchResult(r.id, r.name, r.activeIngredient) for r in cached], has_next

        result = api.search_product(product, page)
        if result:
            has_next = len(result) == api.PAGE_SIZE
            formatted = [
                ProductSearchResult(r['productId'], r['productName'], active_ingredient(r['activeIngredient']))
                for r in result
            ]
            update_cache(product, formatted)
            return formatted, has_next
    return [], has_next


def mims_product_details(product):
    resp = {}
    if product and _is_valid_uuid(product):
        cached = get_product(product)
        if cached and cached.mims:
            return cached._asdict()
        product_details = api.get_product_details(product)
        if product_details:
            mims = ", ".join(product_details['mimsClasses'])
            name = product_details.get('productName', '')
            product_info = ProductInfo(product, name, mims, '')
            resp = update_cache_entry(product_info)._asdict()
    return resp


def _handle_cmi_details(product_id, product_name, cmi_id):
    cmi_details = api.get_cmi_details(cmi_id)
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


def _with_proxied_link(resp):
    if 'link' in resp and resp['link']:
        resp['link'] = f"{reverse('mims_cmi_pdf')}?cmi={resp['cmi_id']}"
    return resp


def mims_cmi_details(product):
    resp = {}
    if product and _is_valid_uuid(product):
        cached = get_cmi_by_product(product)
        if cached and (cached.link or not cached.has_link):
            return _with_proxied_link(cached._asdict())

        resp = {}
        product_details = api.get_product_details(product)
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
                updated = _handle_cmi_details(product, product_name, cmi_info.cmi_id)
                if updated:
                    resp = updated._asdict()
            else:
                resp = cmi_info._asdict()
    return _with_proxied_link(resp)


def fetch_pdf(cmi):
    if cmi and _is_valid_uuid(cmi):
        cached = get_cmi_info(cmi)
        if cached and cached.link:
            return requests.get(cached.link)
    return None
