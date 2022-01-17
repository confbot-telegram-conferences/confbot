# Generated by Django 3.0.11 on 2021-02-04 03:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Enterprise',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', model_utils.fields.AutoCreatedField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='Created at')),
                ('updated_at', model_utils.fields.AutoLastModifiedField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='Updated at')),
                ('name', models.CharField(max_length=255, verbose_name='Name of Enterprise')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserEnterprise',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', model_utils.fields.AutoCreatedField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='Created at')),
                ('updated_at', model_utils.fields.AutoLastModifiedField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='Updated at')),
                ('enterprise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='enterprise.Enterprise')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EnterpriseApp',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', model_utils.fields.AutoCreatedField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='Created at')),
                ('updated_at', model_utils.fields.AutoLastModifiedField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='Updated at')),
                ('apk_key', models.CharField(max_length=255, verbose_name='App Namekey of Enterprise')),
                ('web_hook', models.URLField(blank=True, null=True, verbose_name='Url from enterprise web hook')),
                ('enterprise', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='enterprise.Enterprise')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='enterprise',
            name='members',
            field=models.ManyToManyField(related_name='enterprises', through='enterprise.UserEnterprise', to=settings.AUTH_USER_MODEL),
        ),
    ]