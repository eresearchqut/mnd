# Generated by Django 2.1.9 on 2019-07-16 14:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('patients', '0038_patient_consent_upload_to_change'),
    ]

    operations = [
        migrations.CreateModel(
            name='PatientInsurance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medicare_number', models.CharField(blank=True, max_length=30, null=True)),
                ('pension_number', models.CharField(blank=True, max_length=30, null=True)),
                ('private_health_fund_number', models.CharField(blank=True, max_length=30, null=True)),
                ('ndis_number', models.CharField(blank=True, max_length=30, null=True)),
                ('ndis_plan_manager', models.CharField(choices=[('', 'NDIS Plan Manager'), ('self', 'Self'), ('agency', 'Agency'), ('other', 'Other')], max_length=30)),
                ('ndis_coordinator_first_name', models.CharField(blank=True, max_length=30, null=True)),
                ('ndis_coordinator_last_name', models.CharField(blank=True, max_length=30, null=True)),
                ('ndis_coordinator_phone', models.CharField(blank=True, max_length=30, null=True)),
                ('patient', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='insurance_data', to='patients.Patient')),
            ],
        ),
        migrations.CreateModel(
            name='PreferredContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=30, null=True)),
                ('last_name', models.CharField(blank=True, max_length=30, null=True)),
                ('phone', models.CharField(blank=True, max_length=30, null=True)),
                ('email', models.CharField(blank=True, max_length=30, null=True)),
                ('contact_method', models.CharField(choices=[('', 'Preferred contact method'), ('phone', 'Phone'), ('sms', 'SMS'), ('email', 'Email'), ('primary_carer', 'Primary Carer'), ('person', 'Nominated person below')], max_length=30)),
                ('patient', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='preferred_contact', to='patients.Patient')),
            ],
        ),
        migrations.CreateModel(
            name='PrimaryCarer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('phone', models.CharField(max_length=30)),
                ('email', models.CharField(max_length=30)),
                ('relationship', models.CharField(choices=[('', 'Primary carer relationship'), ('spouse', 'Spouse'), ('child', 'Child'), ('sibling', 'Sibling'), ('friend', 'Friend'), ('other', 'Other(specify)')], max_length=30)),
                ('relationship_info', models.CharField(blank=True, max_length=30, null=True)),
                ('patient', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='primary_carer', to='patients.Patient')),
            ],
        ),
        migrations.CreateModel(
            name='PrivateHealthFund',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=15)),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(max_length=15)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='mnd.PrivateHealthFund')),
            ],
        ),
        migrations.AddField(
            model_name='patientinsurance',
            name='private_health_fund',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mnd.PrivateHealthFund'),
        ),
    ]
