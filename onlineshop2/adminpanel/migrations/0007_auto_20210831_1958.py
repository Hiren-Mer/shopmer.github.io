# Generated by Django 3.2.3 on 2021-08-31 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0006_auto_20210828_1219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='blog_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='testimonial',
            name='testimonial_date',
            field=models.DateField(null=True),
        ),
    ]
