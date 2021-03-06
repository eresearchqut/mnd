# Generated by Django 2.2.13 on 2020-09-15 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0053_patient_carer_link'),
        ('mnd', '0023_mims_product_cache'),
    ]

    operations = [
        migrations.CreateModel(
            name='MIMSCmiCache',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.UUIDField(unique=True)),
                ('product_name', models.CharField(blank=True, max_length=256, null=True)),
                ('cmi_id', models.UUIDField(blank=True, null=True)),
                ('cmi_link', models.CharField(max_length=512)),
                ('has_link', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_on', models.DateTimeField()),
            ],
        ),
    ]
