# Generated by Django 4.0.1 on 2024-03-13 23:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='accounts',
            old_name='accountCurrency',
            new_name='currency',
        ),
        migrations.RenameField(
            model_name='accounts',
            old_name='created_at_registration',
            new_name='isDefault',
        ),
    ]
