# Generated by Django 2.2.9 on 2020-01-16 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0053_patient_carer_link'),
        ('mnd', '0008_primary_carer_remove_relationship_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='primarycarer',
            name='patients',
            field=models.ManyToManyField(related_name='primary_carers', to='patients.Patient'),
        ),
    ]