# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import defaultdict
import json
from django.db import migrations, models



def primary_carer_unique_email(apps, schema_editor):
    PrimaryCarer = apps.get_model('mnd', 'PrimaryCarer')
    PrimaryCarerRelationship = apps.get_model('mnd', 'PrimaryCarerRelationShip')
    Patient = apps.get_model('patients', 'Patient')
    CustomUser = apps.get_model('groups', 'CustomUser')
    carer_email_dict = defaultdict(list)
    for pc in PrimaryCarer.objects.all().order_by('id'):
        carer_email_dict[pc.email.lower()].append(pc)
    multiple_carers = { email: carers for email, carers in carer_email_dict.items() if len(carers) > 1}
    print(f"Found {len(multiple_carers)} email addresses with multiple carers")
    for email, carers in multiple_carers.items():
        with_users = [c for c in carers if CustomUser.objects.filter(username=c.email, is_active=True).exists()]
        has_user = False
        if with_users:
            print(f"Carer {email} has len({with_users}) associated !")
            has_user = True
            to_keep = with_users[0]
        else:
            to_keep = carers[0]
        to_keep.email = email
        to_keep.save()
        to_delete =[c.id for c in carers if c != to_keep]
        # Update users
        Patient.objects.filter(carer_id__in=to_delete).update(carer=to_keep)
        PrimaryCarerRelationship.objects.filter(carer_id__in=to_delete).update(carer=to_keep)
        PrimaryCarer.objects.filter(pk__in=to_delete).delete()
        


class Migration(migrations.Migration):

    dependencies = [
        ('mnd', '0016_auto_20200402_0937'),
    ]

    operations = [
        migrations.RunPython(primary_carer_unique_email, migrations.RunPython.noop)
    ]
