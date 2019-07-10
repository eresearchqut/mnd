import json
import os

from django.utils.translation import gettext as _

def load_insurers_list():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{current_dir}/fixtures/insurers.json") as json_file:
        data = json.load(json_file)
        insurers = [(row['id'], row['insurer']) for row in data]
        return [("", _("Private Health Fund"))] + insurers
