# Generated by Django 5.2.3 on 2025-07-11 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoria',
            name='descripcion',
            field=models.TextField(blank=True, help_text='Descripción breve de la categoría', null=True),
        ),
    ]
