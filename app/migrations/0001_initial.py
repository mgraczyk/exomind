# Generated by Django 2.2.5 on 2019-09-10 17:29

import django.contrib.postgres.fields.citext
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import utils.b64id
import utils.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('email', django.contrib.postgres.fields.citext.CIEmailField(max_length=255, unique=True)),
                ('username', django.contrib.postgres.fields.citext.CIEmailField(max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Reviewable',
            fields=[
                ('id', utils.fields.B64IDField(default=utils.b64id.b64id4, editable=False, primary_key=True, serialize=False)),
                ('url', models.URLField(max_length=4095, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', utils.fields.B64IDField(default=utils.b64id.b64id4, editable=False, primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True, max_length=200, null=True)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('rating', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(5.0)])),
                ('text', models.TextField(blank=True, default='', max_length=65535)),
                ('reviewable', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.Reviewable')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.User')),
            ],
            options={
                'unique_together': {('user', 'reviewable')},
            },
        ),
    ]
