# Generated by Django 2.2 on 2021-01-22 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SysLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=150)),
                ('date', models.DateField(auto_now_add=True)),
                ('description', models.CharField(max_length=300)),
            ],
        ),
    ]
