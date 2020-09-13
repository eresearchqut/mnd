import logging
import requests
import time
import urllib

from django.conf import settings

logger = logging.getLogger(__name__)


class TTLCache:

    class ExpiredEntry(KeyError):
        pass

    def __init__(self, expires_in):
        self.current = int(time.time())
        self.expires_at = self.current + expires_in
        self.store = {}

    def __getitem__(self, name):
        if name in self.store:
            current_ts = int(time.time())
            if current_ts < self.expires_at:
                return self.store[name]
            raise TTLCache.ExpiredEntry("Expired !")
        else:
            raise KeyError(f"No such key: {name}")

    def __setitem__(self, name, value):
        self.store[name] = value


class MIMSService:

    TOKEN_URI = "oauth2/v1/token"
    BRAND_URI = "au/druglist/v1/brands"
    PRODUCT_URI = "au/druglist/v1/products"
    CMI_DETAILS_URI = "au/cmi/v1/cmis"

    def __init__(self):
        self.api_key = settings.MIMS_API_KEY
        self.client_id = settings.MIMS_CLIENT_ID
        self.client_secret = settings.MIMS_CLIENT_SECRET
        self.service_endpoint = settings.MIMS_ENDPOINT
        self.token_cache = None

    def _refresh_token(self):
        url = self._full_url(self.TOKEN_URI)
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        resp = requests.post(url, data=data)
        as_json = resp.json()
        self.token_cache = TTLCache(as_json["expires_in"])
        self.token_cache["access_token"] = as_json["access_token"]

    def _make_auth_header(self):
        if not self.token_cache:
            self._refresh_token()
        try:
            token = self.token_cache["access_token"]
            return {
                "api-key": self.api_key,
                "Authorization": f"Bearer {token}"
            }
        except TTLCache.ExpiredEntry:
            self._refresh_token()

    def _full_url(self, endpoint):
        return f"{self.service_endpoint}/{endpoint}"

    def search_brand(self, brand, page=1, limit=50):
        params = urllib.parse.urlencode({
            "term": brand,
            "include": True,
            "page": page,
            "limit": limit
        })
        resp = requests.get(self._full_url(f"{self.BRAND_URI}?{params}"), headers=self._make_auth_header())
        return resp.json()

    def get_brand_details(self, brand_id):
        fields = urllib.parse.urlencode({
            "fields": "products, mimsClasses"
        })
        resp = requests.get(self._full_url(f"{self.BRAND_URI}/{brand_id}?{fields}"), headers=self._make_auth_header())
        return resp.json()

    def search_product(self, product, page=1, limit=50):
        params = urllib.parse.urlencode({
            "term": product,
            "include": True,
            "page": page,
            "limit": limit
        })
        resp = requests.get(self._full_url(f"{self.PRODUCT_URI}?{params}"), headers=self._make_auth_header())
        return resp.json() if resp.status_code == 200 else {}

    def get_product_details(self, product_id):
        fields = urllib.parse.urlencode({
            "fields": "cmis, brand, productName, mimsClasses"
        })
        resp = requests.get(self._full_url(f"{self.PRODUCT_URI}/{product_id}?{fields}"), headers=self._make_auth_header())
        return resp.json() if resp.status_code == 200 else {}

    def get_cmi_details(self, cmi_id):
        resp = requests.get(self._full_url(f"{self.CMI_DETAILS_URI}/{cmi_id}"), headers=self._make_auth_header())
        return resp.json()
