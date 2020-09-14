from collections import namedtuple
from datetime import timedelta
import logging

from django.utils import timezone

from mnd.models import MIMSCmiCache, MIMSProductCache


logger = logging.getLogger(__name__)


ProductInfo = namedtuple('ProductInfo', 'id name mims activeIngredient')
CMIInfo = namedtuple('CMIInfo', 'product_id name cmi_id link has_link')


def _expiring_ts():
    return timezone.now() + timedelta(days=14)


def _get_existing_products(keys):
    return MIMSProductCache.objects.filter(product_id__in=keys).values_list('product_id', flat=True)


def _get_existing_cmis(keys):
    return MIMSCmiCache.objects.filter(product_id__in=keys).values_list('product_id', flat=True)


def evict_expired_entries():
    MIMSProductCache.objects.filter(expires_on__lt=timezone.now()).delete()
    MIMSCmiCache.objects.filter(expires_on__lt=timezone.now()).delete()


def update_cache(search_term, product_list):
    update_dict = {
        f['id']: ProductInfo(f['id'], f['value'], '', f['activeIngredient']) for f in product_list
    }
    existing = set(str(pid) for pid in _get_existing_products(update_dict.keys()))
    new_entries = {key for key in update_dict.keys() if key not in existing}
    to_add = [
        MIMSProductCache(
            product_id=update_dict[key].id,
            name=update_dict[key].name,
            active_ingredient=update_dict[key].activeIngredient,
            search_term=search_term,
            expires_on=_expiring_ts()
        ) for key in new_entries
    ]
    MIMSProductCache.objects.bulk_create(to_add)
    existing_records = MIMSProductCache.objects.filter(product_id__in=existing)
    for r in existing_records:
        updated_value = update_dict[str(r.product_id)]
        r.active_ingredient = updated_value.activeIngredient
        r.name = updated_value.name
        r.expires_on = _expiring_ts()
        r.save(update_fields=['active_ingredient', 'name', 'expires_on'])

    existing_cmis = set(str(pid) for pid in _get_existing_cmis(update_dict.keys()))
    new_cmis = {key for key in update_dict.keys() if key not in existing_cmis}
    cmis_to_add = [
        MIMSCmiCache(
            product_id=product_id,
            product_name=update_dict[product_id].name,
            cmi_id=None,
            cmi_link='',
            expires_on=_expiring_ts()
        ) for product_id in new_cmis
    ]
    MIMSCmiCache.objects.bulk_create(cmis_to_add)


def get_cache(product_id):
    result = MIMSProductCache.objects.filter(product_id=product_id).first()
    return ProductInfo(result.product_id, result.name, result.mims_classes, result.active_ingredient) if result else None


def get_cmi_cache(product_id):
    cmi = MIMSCmiCache.objects.filter(product_id=product_id).first()
    return CMIInfo(cmi.product_id, cmi.product_name, cmi.cmi_id, cmi.cmi_link, cmi.has_link) if cmi else None


def search_cache(search_term):
    return [
        ProductInfo(r.product_id, r.name, r.mims_classes, r.active_ingredient)
        for r in MIMSProductCache.objects.filter(search_term__iexact=search_term).order_by('name')
    ]


def update_cache_entry(product_info):
    product, created = MIMSProductCache.objects.get_or_create(
        product_id=product_info.id,
        defaults={
            'name': product_info.name,
            'active_ingredient': product_info.activeIngredient,
            'mims_classes': product_info.mims,
            'expires_on': _expiring_ts()
        })
    if not created:
        product.name = product_info.name
        if product_info.activeIngredient:
            product.active_ingredient = product_info.activeIngredient
        if product_info.mims:
            product.mims_classes = product_info.mims
        product.expires_on = _expiring_ts()
        product.save()

    return ProductInfo(product.product_id, product.name, product.mims_classes, product.active_ingredient)


def update_cmi_cache(cmi_info):
    cmi, created = MIMSCmiCache.objects.get_or_create(
        product_id=cmi_info.product_id,
        defaults={
            'product_name': cmi_info.name,
            'cmi_id': cmi_info.cmi_id,
            'cmi_link': cmi_info.link,
            'has_link': cmi_info.has_link,
            'expires_on': _expiring_ts()
        }
    )
    if not created:
        if cmi_info.name:
            cmi.product_name = cmi_info.name
        if cmi_info.cmi_id:
            cmi.cmi_id = cmi_info.cmi_id
        if cmi_info.link:
            cmi.cmi_link = cmi_info.link
        cmi.has_link = cmi_info.has_link
        cmi.save()
    return CMIInfo(cmi.product_id, cmi.product_name, cmi.cmi_id, cmi.cmi_link, cmi.has_link)
