# Generated by Django 4.1.2 on 2022-11-12 21:20

import api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_usermodel_avatar_image_alter_usermodel_chats'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermodel',
            name='display_name',
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name='usermodel',
            name='status',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='usermodel',
            name='avatar_image',
            field=models.ImageField(blank=True, null=True, upload_to=api.models.user_directory_path),
        ),
        migrations.AlterField(
            model_name='usermodel',
            name='chats',
            field=models.ManyToManyField(blank=True, to='api.chatmodel'),
        ),
    ]
