# Generated by Django 3.1.6 on 2021-02-09 10:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.PositiveSmallIntegerField(choices=[('attending', 'The guest will attend the meeting'), ('not attending', 'The guest will not attend the meeting'), ('maybe', "The guest hasn't decided yet")], default=3)),
                ('invitee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MeetingRoom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('from_date', models.DateTimeField()),
                ('to_date', models.DateTimeField()),
                ('attendee', models.ManyToManyField(related_name='meetings', through='reservations.Invitation', to=settings.AUTH_USER_MODEL)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meetings_created', to=settings.AUTH_USER_MODEL)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='reservations.meetingroom')),
            ],
        ),
        migrations.AddField(
            model_name='invitation',
            name='reservation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guests', to='reservations.reservation'),
        ),
    ]