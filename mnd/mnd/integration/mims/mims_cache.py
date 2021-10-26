from cachetools import func
from collections import namedtuple
from datetime import timedelta
import logging

from django.utils import timezone
from django.db.models import F, Min

from mnd.models import MIMSCmiCache, MIMSProductCache, MIMSSearchTerm


logger = logging.getLogger(__name__)


ProductInfo = namedtuple('ProductInfo', 'id name mims activeIngredient')
CMIInfo = namedtuple('CMIInfo', 'product_id name cmi_id cmi_name link has_link')


def _expiring_ts():
    return timezone.now() + timedelta(days=14)


def _get_existing_products(keys):
    return MIMSProductCache.objects.filter(product_id__in=keys).values_list('product_id', flat=True)


def _get_existing_cmis(keys):
    return MIMSCmiCache.objects.filter(product_id__in=keys).values_list('product_id', flat=True)


def _min_ts(input_dict):
    if not input_dict:
        return _expiring_ts()
    return input_dict['expires_on__min']


@func.ttl_cache(maxsize=1, ttl=3600)
def _min_search_expiry_ts():
    return _min_ts(MIMSSearchTerm.objects.aggregate(Min('expires_on')))


@func.ttl_cache(maxsize=1, ttl=3600)
def _min_cmi_expiry_ts():
    return _min_ts(MIMSCmiCache.objects.aggregate(Min('expires_on')))


def write_search_results(search_term, products):
    existing = MIMSSearchTerm.objects.filter(search_term__iexact=search_term).first()
    if existing:
        if existing.expires_on <= timezone.now():
            existing.products = products
            existing.expires_on = _expiring_ts()
            existing.save()
    else:
        MIMSSearchTerm.objects.create(
            search_term=search_term,
            products=products,
            expires_on=_expiring_ts()
        )


def evict_expired_entries():
    if (min_expiry := _min_search_expiry_ts()) and timezone.now() > min_expiry:
        search_term_qs = MIMSSearchTerm.objects.filter(expires_on__lt=timezone.now())
        logger.info(f"About to evict {search_term_qs.count()} search term entries")
        for st in search_term_qs:
            # Updates are performed individually to prevent deadlocks on start
            for product in MIMSProductCache.objects.filter(product_id__in=st.products):
                product.ref_count -= 1
                product.save(update_fields=["ref_count"])
        search_term_qs.delete()
        products_to_delete = MIMSProductCache.objects.filter(ref_count__lte=0)
        logger.info(f"Deleting {products_to_delete.count()} products with no references")
        products_to_delete.delete()
        _min_search_expiry_ts.cache_clear()
    if (min_expiry := _min_cmi_expiry_ts()) and timezone.now() > min_expiry:
        cmi_cache_qs = MIMSCmiCache.objects.filter(expires_on__lt=timezone.now())
        logger.info(f"Evicting {cmi_cache_qs.count()} cmi cache entries")
        cmi_cache_qs.delete()
        _min_cmi_expiry_ts.cache_clear()


def update_cache(search_term, product_list):
    update_dict = {
        f.id: ProductInfo(f.id, f.value, '', f.activeIngredient) for f in product_list
    }
    existing = set(str(pid) for pid in _get_existing_products(update_dict.keys()))
    new_entries = {key for key in update_dict.keys() if key not in existing}
    to_add = [
        MIMSProductCache(
            product_id=update_dict[key].id,
            name=update_dict[key].name,
            active_ingredient=update_dict[key].activeIngredient,
        ) for key in new_entries
    ]
    MIMSProductCache.objects.bulk_create(to_add)
    existing_records = MIMSProductCache.objects.filter(product_id__in=existing)
    for r in existing_records:
        updated_value = update_dict[str(r.product_id)]
        r.active_ingredient = updated_value.activeIngredient
        r.name = updated_value.name
        r.ref_count = r.ref_count + 1
        r.save(update_fields=['active_ingredient', 'name', 'ref_count'])


def get_product(product_id):
    result = MIMSProductCache.objects.filter(product_id=product_id).first()
    return ProductInfo(result.product_id, result.name, result.mims_classes, result.active_ingredient) if result else None


def get_cmis_by_product(product_id):
    cmis = MIMSCmiCache.objects.filter(product_id=product_id)
    return [
        CMIInfo(cmi.product_id, cmi.product_name, cmi.cmi_id, cmi.cmi_name, cmi.cmi_link, cmi.has_link) for cmi in cmis
    ]


def get_cmi_info(cmi_id):
    cmi = MIMSCmiCache.objects.filter(cmi_id=cmi_id).first()
    return CMIInfo(cmi.product_id, cmi.product_name, cmi.cmi_id, cmi.cmi_name, cmi.cmi_link, cmi.has_link) if cmi else None


def search_cache(search_term):
    result = MIMSSearchTerm.objects.filter(search_term__iexact=search_term, expires_on__gte=timezone.now()).first()
    if not result:
        return []
    return [
        ProductInfo(r.product_id, r.name, r.mims_classes, r.active_ingredient)
        for r in MIMSProductCache.objects.filter(product_id__in=result.products).order_by('name')
    ]


def update_cache_entry(product_info):
    product, created = MIMSProductCache.objects.get_or_create(
        product_id=product_info.id,
        defaults={
            'name': product_info.name,
            'active_ingredient': product_info.activeIngredient,
            'mims_classes': product_info.mims,
        })
    if not created:
        product.name = product_info.name
        if product_info.activeIngredient:
            product.active_ingredient = product_info.activeIngredient
        if product_info.mims:
            product.mims_classes = product_info.mims
        product.save()

    return ProductInfo(product.product_id, product.name, product.mims_classes, product.active_ingredient)


def update_cmi_cache(cmi_info):
    cmi, created = MIMSCmiCache.objects.get_or_create(
        product_id=cmi_info.product_id,
        cmi_id=cmi_info.cmi_id,
        defaults={
            'product_name': cmi_info.name,
            'cmi_name': cmi_info.cmi_name,
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
        if cmi_info.cmi_name:
            cmi.cmi_name = cmi_info.cmi_name
        cmi.has_link = cmi_info.has_link
        cmi.save()
    return CMIInfo(cmi.product_id, cmi.product_name, cmi.cmi_id, cmi.cmi_name, cmi.cmi_link, cmi.has_link)
