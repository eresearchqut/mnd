# Generated by Django 2.2.24 on 2021-11-10 13:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mnd', '0033_optional_insurance_fields'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MIMSCmiCache',
        ),
        migrations.DeleteModel(
            name='MIMSProductCache',
        ),
        migrations.DeleteModel(
            name='MIMSSearchTerm',
        ),
    ]
