# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-02 11:50
from __future__ import unicode_literals

from django.db import migrations


def forwards_func(apps, schema_editor):
    """Creates the permissions "Manage curriculum" and "Consume curriculum"."""

    from nanou.permissions import GlobalPermission

    db_alias = schema_editor.connection.alias

    GlobalPermission.objects.create_global(
        db_alias=db_alias,
        codename='manage_curriculum',
        name='Manage curriculum',
    )
    GlobalPermission.objects.create_global(
        db_alias=db_alias,
        codename='consume_curriculum',
        name='Consume curriculum',
    )


def reverse_func(apps, schema_editor):
    """Deletes the permissions "Manage curriculum" and "Consume curriculum"."""
    Permission = apps.get_model('auth', 'Permission')
    db_alias = schema_editor.connection.alias
    Permission.objects.using(db_alias).filter(name='Manage curriculum').delete()
    Permission.objects.using(db_alias).filter(name='Consume curriculum').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func)
    ]
