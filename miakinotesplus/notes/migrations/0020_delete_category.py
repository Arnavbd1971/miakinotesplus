# Generated by Django 3.2.9 on 2021-11-28 07:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0019_category'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Category',
        ),
    ]