# Generated by Django 5.1.1 on 2024-11-06 00:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0005_event_attendees_alter_event_organizer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='time_finish',
            field=models.TimeField(default='23:59:59'),
        ),
    ]
