# Generated by Django 3.0.11 on 2021-05-22 23:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('conference', '0007_auto_20210511_1612'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conference',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='conferences', to='conference.Course'),
        ),
    ]
