
# Generated by Django 4.0.3 on 2023-09-09 04:57

from django.db import migrations
from ..models import *

def add_initial_roles(apps, schema_editor):
    admin_role = Role(name='Admin')
    admin_role.save()
    company_role = Role(name='Company')
    company_role.save()
    employee_role = Role(name='Employee')
    employee_role.save()
    candidate_role = Role(name='Candidate')
    candidate_role.save()

def remove_initial_roles(apps, schema_editor):
    Role = apps.get_model('jobs', 'Role')
    Role.objects.all().delete()
class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0005_alter_company_logo'),
    ]

    operations = [
        migrations.RunPython(add_initial_roles, remove_initial_roles),

    ]
