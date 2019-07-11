'''A large list of genes.'''

import os
from mnd.models import PrivateHealthFund
from django.core import serializers


def load_data(**kwargs):
    filename = os.path.join(os.path.dirname(__file__), 'private_health_fund.json')
    with open(filename) as f:
        for fund in serializers.deserialize('json', f):
            fund.save()
