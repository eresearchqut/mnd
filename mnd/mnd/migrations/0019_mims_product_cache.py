# Generated by Django 2.2.13 on 2020-09-14 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mnd', '0018_primary_carer_email_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='MIMSProductCache',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.UUIDField(unique=True)),
                ('name', models.CharField(max_length=256)),
                ('active_ingredient', models.TextField()),
                ('mims_classes', models.TextField()),
                ('search_term', models.CharField(blank=True, max_length=32, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_on', models.DateTimeField()),
            ],
        ),
        migrations.AddIndex(
            model_name='mimsproductcache',
            index=models.Index(fields=['search_term'], name='mnd_mimspro_search__5f0763_idx'),
        ),
        migrations.AddIndex(
            model_name='mimsproductcache',
            index=models.Index(fields=['name'], name='mnd_mimspro_name_c63fd4_idx'),
        ),
    ]
