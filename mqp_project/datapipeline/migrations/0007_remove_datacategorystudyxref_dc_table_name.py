# Generated by Django 3.1.2 on 2021-03-02 02:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datapipeline', '0006_auto_20210124_2036'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datacategorystudyxref',
            name='dc_table_name',
        ),
    ]
