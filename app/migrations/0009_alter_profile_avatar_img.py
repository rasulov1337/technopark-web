# Generated by Django 5.0.3 on 2024-04-09 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_profile_answers_counter_profile_questions_counter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar_img',
            field=models.ImageField(blank=True, default='static/img/avatar.png', null=True, upload_to='uploads/'),
        ),
    ]
