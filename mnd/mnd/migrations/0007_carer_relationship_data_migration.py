# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.db import migrations, models



def migrate_carer_relationship(apps, schema_editor):
    PrimaryCarer = apps.get_model('mnd', 'PrimaryCarer')
    PrimaryCarerRelationship = apps.get_model('mnd', 'PrimaryCarerRelationship')
    for pc in PrimaryCarer.objects.all():
        PrimaryCarerRelationship.objects.create(
            carer=pc,
            patient=pc.patient,
            relationship=pc.relationship,
            relationship_info=pc.relationship_info
        )


class Migration(migrations.Migration):

    dependencies = [
        ('mnd', '0006_primarycarerrelationship'),
    ]

    operations = [
        migrations.RunPython(migrate_carer_relationship, migrations.RunPython.noop)
    ]
