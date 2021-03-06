# Generated by Django 2.2.9 on 2020-01-15 16:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0053_patient_carer_link'),
        ('mnd', '0005_carerregistration'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrimaryCarerRelationship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relationship', models.CharField(choices=[('', 'Primary carer relationship'), ('spouse', 'Spouse'), ('child', 'Child'), ('sibling', 'Sibling'), ('friend', 'Friend'), ('other', 'Other(specify)')], max_length=30)),
                ('relationship_info', models.CharField(blank=True, max_length=30, null=True)),
                ('carer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relation', to='mnd.PrimaryCarer')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carer_relation', to='patients.Patient')),
            ],
        ),
    ]
