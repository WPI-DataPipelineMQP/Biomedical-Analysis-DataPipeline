# Generated by Django 3.1.2 on 2020-12-13 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datapipeline', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='datacategory',
            name='subject_organization',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
