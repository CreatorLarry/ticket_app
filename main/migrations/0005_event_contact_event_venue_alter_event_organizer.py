# Generated by Django 5.1.7 on 2025-05-13 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_alter_organizer_managers_alter_organizer_is_active_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='contact',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='venue',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='organizer',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
