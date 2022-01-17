# Generated by Django 3.0.11 on 2021-06-06 16:49

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conference', '0008_auto_20210522_2345'),
    ]

    operations = [
        migrations.AddField(
            model_name='slide',
            name='image_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True, verbose_name='Image Data'),
        ),
        migrations.AddField(
            model_name='slide',
            name='image_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Image Id'),
        ),
        migrations.AddField(
            model_name='slide',
            name='voice_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True, verbose_name='Voice Data'),
        ),
        migrations.AddField(
            model_name='slide',
            name='voice_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Voice Id'),
        ),
    ]
