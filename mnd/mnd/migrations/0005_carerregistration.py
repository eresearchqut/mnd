# Generated by Django 2.2.9 on 2020-01-14 15:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mnd', '0004_primary_carer_new_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='CarerRegistration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField()),
                ('expires_on', models.DateTimeField()),
                ('status', models.CharField(choices=[('created', 'created'), ('registered', 'registered'), ('approved', 'approved'), ('rejected', 'rejected')], default='created', max_length=16)),
                ('carer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mnd.PrimaryCarer')),
            ],
        ),
    ]
