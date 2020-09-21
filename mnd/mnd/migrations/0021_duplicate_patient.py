# Generated by Django 2.2.13 on 2020-09-17 13:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0053_patient_carer_link'),
        ('mnd', '0020_mnd_models_data_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='DuplicatePatient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_duplicate', models.BooleanField(default=False)),
                ('patient', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='duplicate_patient', to='patients.Patient')),
            ],
        ),
    ]