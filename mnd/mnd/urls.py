from django.conf.urls import include
from django.urls import re_path

from . import views

urlpatterns = [
    # Any custom URLs go here before we include the TRRF urls
    re_path(r"^pdf/about_me/(?P<registry_code>\w+)/(?P<patient_id>\d+)/?$", views.pdf_export, name='pdf-export'),
    re_path(r'', include('rdrf.urls')),
]
