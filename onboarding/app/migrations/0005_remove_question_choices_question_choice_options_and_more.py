# Generated by Django 5.0.2 on 2024-03-01 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_surveysection_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='choices',
        ),
        migrations.AddField(
            model_name='question',
            name='choice_options',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='type',
            field=models.CharField(choices=[('text', 'Text'), ('choice', 'Choice')], default='text', max_length=50),
        ),
    ]
