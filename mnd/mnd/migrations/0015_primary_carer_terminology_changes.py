# Generated by Django 2.2.9 on 2020-03-30 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mnd', '0014_primary_carer_relationship_unique_patient'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preferredcontact',
            name='contact_method',
            field=models.CharField(choices=[('', 'Preferred contact method'), ('phone', 'Phone'), ('sms', 'SMS'), ('email', 'Email'), ('primary_carer', 'Principal Caregiver'), ('person', 'Nominated person below')], max_length=30),
        ),
        migrations.AlterField(
            model_name='primarycarerrelationship',
            name='relationship',
            field=models.CharField(choices=[('', 'Principal Caregiver relationship'), ('spouse', 'Spouse'), ('child', 'Child'), ('sibling', 'Sibling'), ('friend', 'Friend'), ('other', 'Other(specify)')], max_length=30),
        ),
    ]
