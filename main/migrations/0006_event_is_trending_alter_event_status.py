# Generated by Django 5.1.7 on 2025-05-13 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_event_contact_event_venue_alter_event_organizer'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='is_trending',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='event',
            name='status',
            field=models.CharField(choices=[('upcoming', 'Upcoming'), ('trending', 'Trending'), ('expired', 'Expired')], default='Upcoming', max_length=20),
        ),
    ]
