# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-04-29 11:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RecipeManager', '0002_auto_20170201_2326'),
    ]

    operations = [
        migrations.AddField(
            model_name='version',
            name='change_note',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='version',
            name='method',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='version',
            name='result_note',
            field=models.TextField(blank=True, null=True),
        ),
    ]
