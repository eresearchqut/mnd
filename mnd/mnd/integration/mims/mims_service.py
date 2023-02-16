from collections import namedtuple
import logging
import requests
import uuid

from cache_memoize import cache_memoize
from django.shortcuts import reverse

from .mims_api import MIMSApi

MAX_SEARCH_PAGES = 5
MIN_SEARCH_STRING_LENGTH = 4
CMI_DOCUMENT_FORMATS = ('pdf', 'reducedpdf')
CACHE_TIMEOUT = 3600

ProductSearchResult = namedtuple('ProductSearchResult', 'id value activeIngredient')
ProductInfo = namedtuple('ProductInfo', 'id name mims activeIngredient cmis')
CMIInfo = namedtuple('CMIInfo', 'cmi_id cmi_name link')

logger = logging.getLogger(__name__)

api = MIMSApi()


def _is_valid_uuid(input_str):
    try:
        uuid.UUID(input_str)
    except Exception:
        return False
    return True


@cache_memoize(CACHE_TIMEOUT)
def mims_product_search(product):
    return list(mims_product_iter(product))


def mims_product_iter(product):
    def active_ingredient(result):
        return ", ".join(result.split(" + ")) if result else ''

    if product and product.strip() != '' and len(product) >= MIN_SEARCH_STRING_LENGTH:
        for page in range(1, MAX_SEARCH_PAGES):
            result = api.search_product(product, page)
            if not result:
                break
            for product in result:
                yield ProductSearchResult(product['productId'],
                                          product['productName'],
                                          active_ingredient(product['activeIngredient']))
            if len(result) != api.PAGE_SIZE:
                break


@cache_memoize(CACHE_TIMEOUT)
def mims_product_details(product):
    if product and _is_valid_uuid(product):
        product_details = api.get_product_details(product)
        if product_details:
            mims = ", ".join(product_details['mimsClasses'])
            name = product_details.get('productName', '')

            active_ingredient = next(iter(product_details.get("acgs", [])), {'acgName': None}).get("acgName")
            cmis = product_details.get("cmis", [])

            return ProductInfo(product, name, mims, active_ingredient, cmis)
    return None


@cache_memoize(CACHE_TIMEOUT)
def mims_cmi_details(cmi):
    cmi_details = api.get_cmi_details(cmi)
    if cmi_details:
        cmi_name = cmi_details.get('cmiName')
        document = next((d for d in cmi_details['cmiDocuments'] if d['cmiFormat'] in CMI_DOCUMENT_FORMATS), None)

        return CMIInfo(cmi, cmi_name, document['cmiDocument'])
    return None


def mims_product_cmis(product):
    result = []
    product_name = None
    if product and _is_valid_uuid(product):
        product_details = mims_product_details(product)
        if product_details:
            product_name = product_details.name
            for cmi in product_details.cmis:
                cmi_id = cmi['cmiId']
                if cmi_id:
                    cmi_details = mims_cmi_details(cmi_id)
                    if cmi_details:
                        result.append(cmi_details._replace(link=f"{reverse('mims_cmi_pdf')}?cmi={cmi_id}"))

    return product_name, result


def fetch_pdf(cmi):
    if cmi and _is_valid_uuid(cmi):
        details = mims_cmi_details(cmi)
        if details and details.link:
            return requests.get(details.link)
    return None
