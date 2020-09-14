from collections import namedtuple
from datetime import timedelta
import logging

from django.utils import timezone

from mnd.models import MIMSProductCache


logger = logging.getLogger(__name__)


ProductInfo = namedtuple('ProductInfo', 'id name mims activeIngredient')


def _expiring_ts():
    return timezone.now() + timedelta(days=14)


def update_cache(search_term, product_list):
    update_dict = {
        f['id']: ProductInfo(f['id'], f['value'], '', f['activeIngredient']) for f in product_list
    }
    existing = set(
        str(pid) for pid in
        MIMSProductCache.objects.filter(product_id__in=update_dict.keys()).values_list('product_id', flat=True)
    )
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


def get_cache(product_id):
    result = MIMSProductCache.objects.filter(product_id=product_id).first()
    return ProductInfo(result.id, result.name, result.mims_classes, result.active_ingredient) if result else None


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
