# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdministrativeArea',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='name')),
                ('old_names', models.CharField(max_length=200, null=True, verbose_name='old names', blank=True)),
                ('slug', models.CharField(max_length=255, verbose_name='slug')),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('abolished_date', models.DateField(null=True, verbose_name='abolished date', blank=True)),
                ('is_county_level_city', models.BooleanField(default=False, verbose_name='is county level city')),
                ('administrative_level', models.SmallIntegerField(null=True, verbose_name='administrative level', blank=True)),
                ('alternative_names', models.CharField(max_length=255, verbose_name='alternative names')),
                ('short_name', models.CharField(max_length=50, verbose_name='short name')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AreaProperty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=3, null=True, verbose_name='country_code', blank=True)),
                ('population', models.IntegerField(null=True, verbose_name='population', blank=True)),
                ('area', models.IntegerField(null=True, verbose_name='area', blank=True)),
                ('currency', models.CharField(max_length=3, null=True, verbose_name='currency', blank=True)),
                ('continent', models.CharField(max_length=2, null=True, verbose_name='continent', blank=True)),
                ('capital', models.CharField(max_length=100, null=True, verbose_name='capital', blank=True)),
                ('tld', models.CharField(max_length=5, null=True, verbose_name='tld', blank=True)),
                ('yt_importance', models.SmallIntegerField(default=1, null=True, verbose_name='yt importance', blank=True)),
                ('is_municipalities', models.BooleanField(default=False, verbose_name='is municipalities')),
                ('is_provincial_capital', models.BooleanField(default=False, verbose_name='is provincial capital')),
                ('is_special_administrative_region', models.BooleanField(default=False, verbose_name='is special administrative region')),
                ('zipcode', models.CharField(max_length=25, null=True, verbose_name='zipcode')),
            ],
            options={
                'ordering': ['-yt_importance'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='administrativearea',
            name='area_property',
            field=models.OneToOneField(null=True, blank=True, to='locations.AreaProperty', verbose_name='area property'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='administrativearea',
            name='parent',
            field=mptt.fields.TreeForeignKey(related_name='children', verbose_name='parent', blank=True, to='locations.AdministrativeArea', null=True),
            preserve_default=True,
        ),
    ]
