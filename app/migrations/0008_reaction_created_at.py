# Generated by Django 3.1.5 on 2021-02-16 22:38

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_auto_20210124_2228'),
    ]

    operations = [
        migrations.AddField(
            model_name='reaction',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
