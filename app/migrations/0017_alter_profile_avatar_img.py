# Generated by Django 5.0.4 on 2024-05-14 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_profile_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar_img',
            field=models.ImageField(blank=True, default='img/avatar.png', null=True, upload_to='images'),
        ),
    ]
