# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-03-26 18:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='anime',
            name='members',
            field=models.IntegerField(default=None),
            preserve_default=False,
        ),
    ]
