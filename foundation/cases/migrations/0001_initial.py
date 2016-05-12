# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-12 08:41
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from=b'name', unique=True, verbose_name='Slug')),
                ('receiving_email', models.CharField(help_text='Address used to receiving emails.', max_length=150, verbose_name='Receiving email')),
            ],
            options={
                'ordering': ['created'],
                'verbose_name': 'Case',
                'verbose_name_plural': 'Cases',
            },
        ),
    ]
