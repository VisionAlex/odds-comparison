# Generated by Django 3.1.7 on 2021-03-10 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('odds', '0003_runner_tonybet_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='favbet_code',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='runner',
            name='favbet_name',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
