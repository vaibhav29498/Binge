# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-03-26 15:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Anime',
            fields=[
                ('aid', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('rating', models.DecimalField(decimal_places=2, max_digits=4)),
            ],
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('gid', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name='anime',
            name='genre',
            field=models.ManyToManyField(to='recommender.Genre'),
        ),
        migrations.AddField(
            model_name='anime',
            name='related',
            field=models.ManyToManyField(related_name='_anime_related_+', to='recommender.Anime'),
        ),
    ]
