# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-21 12:49
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models

import weblate.utils.fields


class Migration(migrations.Migration):

    replaces = [
        ("addons", "0001_initial"),
        ("addons", "0002_auto_20180203_2258"),
        ("addons", "0003_install_addons"),
        ("addons", "0004_auto_20180309_1300"),
        ("addons", "0005_unwrapped_po"),
        ("addons", "0006_addon_project_scope"),
    ]

    initial = True

    dependencies = [("trans", "0122_auto_20180129_1507")]

    operations = [
        migrations.CreateModel(
            name="Addon",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("configuration", weblate.utils.fields.JSONField()),
                ("state", weblate.utils.fields.JSONField()),
                (
                    "component",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="trans.Component",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "event",
                    models.IntegerField(
                        choices=[
                            (1, "post push"),
                            (2, "post update"),
                            (3, "pre commit"),
                            (4, "post commit"),
                            (5, "post add"),
                            (6, "unit post create"),
                            (7, "store post load"),
                        ]
                    ),
                ),
                (
                    "addon",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="addons.Addon"
                    ),
                ),
            ],
        ),
        migrations.AlterUniqueTogether(
            name="event", unique_together={("addon", "event")}
        ),
        migrations.AddField(
            model_name="addon",
            name="project_scope",
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterUniqueTogether(
            name="addon", unique_together={("component", "name")}
        ),
    ]
