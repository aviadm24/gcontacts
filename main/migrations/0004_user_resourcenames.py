# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-11-01 07:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20191023_1031'),
    ]

    operations = [
        migrations.CreateModel(
            name='User_resourceNames',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resource_name', models.CharField(max_length=1000)),
                ('etag', models.CharField(max_length=1000)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.User_tokens')),
            ],
        ),
    ]