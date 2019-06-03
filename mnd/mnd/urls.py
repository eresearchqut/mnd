from django.conf.urls import include
from django.urls import re_path


urlpatterns = [
    # Any custom URLs go here before we include the TRRF urls
    re_path(r'', include('rdrf.urls')),
]
