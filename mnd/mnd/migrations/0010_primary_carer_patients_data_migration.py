# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.db import migrations, models



def migrate_carer_patient(apps, schema_editor):
    PrimaryCarer = apps.get_model('mnd', 'PrimaryCarer')
    for pc in PrimaryCarer.objects.all():
        pc.patients.add(pc.patient)


class Migration(migrations.Migration):

    dependencies = [
        ('mnd', '0009_primarycarer_patients'),
    ]

    operations = [
        migrations.RunPython(migrate_carer_patient, migrations.RunPython.noop)
    ]
