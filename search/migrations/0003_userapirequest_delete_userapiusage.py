# Generated by Django 5.1.1 on 2024-09-15 04:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0002_userapiusage'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAPIRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(unique=True)),
                ('request_count', models.IntegerField(default=0)),
                ('last_request_time', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.DeleteModel(
            name='UserAPIUsage',
        ),
    ]
