# Generated by Django 5.0.3 on 2024-04-08 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_questionlike_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionlike',
            name='status',
            field=models.CharField(choices=[(-1, 'Disliked'), (1, 'Liked')], max_length=2),
        ),
    ]