# Generated by Django 4.2.15 on 2024-09-03 01:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('l4m_app', '0006_bet_expiration_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bet',
            name='Name',
        ),
    ]
