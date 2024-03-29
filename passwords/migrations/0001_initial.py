# Generated by Django 2.2 on 2021-01-04 13:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscription_amount', models.PositiveIntegerField(default=1)),
                ('free_trial_length', models.PositiveIntegerField(default=30)),
                ('quick_retrieval_amount', models.PositiveIntegerField(default=20)),
            ],
        ),
        migrations.CreateModel(
            name='Subscriber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sign_up_date', models.DateField(auto_now_add=True)),
                ('customer_token', models.CharField(blank=True, max_length=150, null=True)),
                ('payment_method_token', models.CharField(blank=True, max_length=150, null=True)),
                ('subscription_token', models.CharField(blank=True, max_length=150, null=True)),
                ('subscription_active', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Password',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.BinaryField(editable=True, max_length=300)),
                ('username', models.BinaryField(editable=True, max_length=300)),
                ('hashed_password', models.BinaryField(editable=True, max_length=300)),
                ('challenge_time', models.PositiveIntegerField()),
                ('number_of_retrieves', models.PositiveIntegerField(default=0)),
                ('number_of_instant_unlocks', models.PositiveIntegerField(default=0)),
                ('number_of_attempted_retrieves', models.PositiveIntegerField(default=0)),
                ('subscriber', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='passwords.Subscriber')),
            ],
        ),
    ]
