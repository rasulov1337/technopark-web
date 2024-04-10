# Generated by Django 5.0.3 on 2024-04-08 14:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='question',
            old_name='tag',
            new_name='tags',
        ),
        migrations.AddField(
            model_name='question',
            name='score',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='question',
            name='status',
            field=models.CharField(choices=[('S', 'Solved'), ('N', 'Not Solved')], default='N', max_length=1),
        ),
        migrations.CreateModel(
            name='AnswerLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('D', 'Disliked'), ('L', 'Liked')], max_length=1)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('answer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.answer')),
                ('author', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='app.profile')),
                ('question', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.question')),
            ],
            options={
                'unique_together': {('author', 'answer')},
            },
        ),
        migrations.CreateModel(
            name='QuestionLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('D', 'Disliked'), ('L', 'Liked')], max_length=1)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('author', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='app.profile')),
                ('question', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.question')),
            ],
            options={
                'unique_together': {('author', 'question')},
            },
        ),
        migrations.DeleteModel(
            name='Like',
        ),
    ]