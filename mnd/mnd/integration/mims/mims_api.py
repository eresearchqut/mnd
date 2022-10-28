from cachetools import TTLCache
import functools
import logging
import requests
import urllib

from django.conf import settings

from mnd.models import MIMSProductCache, MIMSCMICache

logger = logging.getLogger(__name__)


def cached_lookup(model):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(self, uuid):
            response = fn(self, uuid)
            if response:
                model.objects.update_or_create(uuid=uuid, defaults={'data': response})
            else:
                cached_value = model.objects.filter(uuid=uuid).first()
                if cached_value:
                    response = cached_value.data
            return response
        return wrapper
    return decorator


class MIMSApi:

    PAGE_SIZE = 50

    TOKEN_URI = "oauth2/v1/token"
    PRODUCT_URI = "au/druglist/v1/products"
    CMI_DETAILS_URI = "au/cmi/v1/cmis"

    def __init__(self):
        self.api_key = settings.MIMS_API_KEY
        self.client_id = settings.MIMS_CLIENT_ID
        self.client_secret = settings.MIMS_CLIENT_SECRET
        self.service_endpoint = settings.MIMS_ENDPOINT
        self.token_cache = None

    def _refresh_token(self):
        self.token_cache = None
        url = self._full_url(self.TOKEN_URI)
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        try:
            resp = requests.post(url, data=data)
            as_json = resp.json()
            expires_in = as_json["expires_in"]
            self.token_cache = TTLCache(1, expires_in)
            self.token_cache["access_token"] = as_json["access_token"]
        except requests.exceptions.RequestException as e:
            logger.exception("Exception while refreshing token", e)

    def _make_auth_header(self):
        if not self.token_cache:
            self._refresh_token()
        try:
            token = self.token_cache["access_token"]
            return {
                "api-key": self.api_key,
                "Authorization": f"Bearer {token}"
            }
        except KeyError:
            self._refresh_token()

    def _full_url(self, endpoint):
        return f"{self.service_endpoint}/{endpoint}"

    def search_product(self, product, page, limit=PAGE_SIZE):
        params = urllib.parse.urlencode({
            "term": product,
            "include": True,
            "page": page,
            "limit": limit
        })
        try:
            resp = requests.get(self._full_url(f"{self.PRODUCT_URI}?{params}"), headers=self._make_auth_header())
            return resp.json() if resp.status_code == 200 else {}
        except requests.exceptions.RequestException as e:
            logger.exception("Exception while searching for products", e)
            return {}

    @cached_lookup(MIMSProductCache)
    def get_product_details(self, product_id):
        fields = urllib.parse.urlencode({
            "fields": "cmis, brand, productName, mimsClasses, acgs"
        })
        try:
            resp = requests.get(self._full_url(f"{self.PRODUCT_URI}/{product_id}?{fields}"), headers=self._make_auth_header())
            return resp.json() if resp.status_code == 200 else {}
        except requests.exceptions.RequestException as e:
            logger.exception("Exception while fetching product details", e)
            return {}

    @cached_lookup(MIMSCMICache)
    def get_cmi_details(self, cmi_id):
        try:
            resp = requests.get(self._full_url(f"{self.CMI_DETAILS_URI}/{cmi_id}"), headers=self._make_auth_header())
            return resp.json() if resp.status_code == 200 else {}
        except requests.exceptions.RequestException as e:
            logger.exception("Exception while getting cmi details", e)
            return {}
