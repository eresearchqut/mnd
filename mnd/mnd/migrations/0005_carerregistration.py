# Generated by Django 2.2.9 on 2020-01-15 16:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0053_patient_carer_link'),
        ('mnd', '0004_primary_carer_new_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='CarerRegistration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField()),
                ('status', models.CharField(choices=[('created', 'created'), ('registered', 'registered'), ('deactivated', 'deactivated')], default='created', max_length=16)),
                ('expires_on', models.DateTimeField()),
                ('registration_ts', models.DateTimeField(blank=True, null=True)),
                ('carer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mnd.PrimaryCarer')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patients.Patient')),
            ],
        ),
    ]
