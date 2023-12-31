# Generated by Django 4.0.3 on 2023-09-27 02:32

import ckeditor.fields
from django.db import migrations, models
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

        migrations.RemoveField(
            model_name='job',
            name='degree_required',
        ),
        migrations.AddField(
            model_name='user',
            name='auth_provider',
            field=models.CharField(default='default', max_length=255),
        ),
        migrations.AlterField(
            model_name='application',
            name='cover_letter',
            field=ckeditor.fields.RichTextField(),
        ),
        migrations.AlterField(
            model_name='curriculum_vitae',
            name='foreignLanguage',
            field=ckeditor.fields.RichTextField(),
        ),
        migrations.AlterField(
            model_name='job',
            name='description',
            field=ckeditor.fields.RichTextField(),
        ),
        migrations.AlterField(
            model_name='job',
            name='job_required',
            field=ckeditor.fields.RichTextField(),
        ), migrations.RunPython(add_initial_roles, remove_initial_roles),

    ]
