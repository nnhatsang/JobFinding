# Generated by Django 4.2.3 on 2023-08-01 07:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_alter_company_user_alter_employee_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='imagecompany',
            old_name='tour',
            new_name='company',
        ),
    ]
