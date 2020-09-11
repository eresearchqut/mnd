# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import defaultdict
from django.db import migrations
from django.db.models import Q


def migrate_mnd_data(apps, schema_editor):
    PatientInsurance = apps.get_model('mnd', 'PatientInsurance')

    private_health_fund_set = (
        Q(private_health_fund_number__isnull=False)
        | ~(Q(private_health_fund__isnull=True) | Q(private_health_fund__iexact=''))
    )
    PatientInsurance.objects.filter(private_health_fund_set).update(has_private_health_fund=True)
    ndis_number_set = Q(ndis_number__isnull=False) & ~Q(ndis_number__iexact='')
    PatientInsurance.objects.filter(ndis_number_set).update(is_ndis_participant=True)
    with_dva_card = (
        Q(dva_card_number__isnull=False)
        | ~(Q(dva_card_type__iexact='') | Q(dva_card_type__isnull=True))
    )
    PatientInsurance.objects.filter(with_dva_card).update(has_dva_card=True)


class Migration(migrations.Migration):

    dependencies = [
        ('mnd', '0019_update_mnd_models_fields'),
    ]

    operations = [
        migrations.RunPython(migrate_mnd_data, migrations.RunPython.noop)
    ]
