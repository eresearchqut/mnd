# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def cleanup_mims_cmi_cache(apps, schema_editor):
    MIMSCmiCache = apps.get_model('mnd', 'MIMSCmiCache')
    MIMSCmiCache.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('mnd', '0026_mims_search_term_table'),
    ]

    operations = [
        migrations.RunPython(cleanup_mims_cmi_cache, migrations.RunPython.noop)
    ]
