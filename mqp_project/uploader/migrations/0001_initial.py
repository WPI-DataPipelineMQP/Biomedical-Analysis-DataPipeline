# Generated by Django 3.1.2 on 2020-12-09 01:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('datapipeline', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=250)),
                ('data_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='datapipeline.datacategory')),
            ],
            options={
                'db_table': 'Document',
            },
        ),
    ]
