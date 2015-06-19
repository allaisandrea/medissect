# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Procedure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('allowed_amount', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='ProcedureDescriptor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=5)),
                ('descriptor', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_name', models.CharField(max_length=20)),
                ('first_name', models.CharField(max_length=20)),
                ('address1', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='procedure',
            name='descriptor',
            field=models.ForeignKey(to='explorer.ProcedureDescriptor'),
        ),
        migrations.AddField(
            model_name='procedure',
            name='provider',
            field=models.ForeignKey(to='explorer.Provider'),
        ),
    ]
