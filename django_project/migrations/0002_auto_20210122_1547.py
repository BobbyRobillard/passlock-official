# Generated by Django 2.2 on 2021-01-22 20:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_project', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SysLog',
            new_name='ErrorLog',
        ),
    ]
