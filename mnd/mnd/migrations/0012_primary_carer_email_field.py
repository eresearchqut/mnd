# Generated by Django 2.2.9 on 2020-03-12 02:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mnd', '0011_remove_primarycarer_patient'),
    ]

    operations = [
        migrations.AlterField(
            model_name='primarycarer',
            name='email',
            field=models.EmailField(max_length=30),
        ),
    ]