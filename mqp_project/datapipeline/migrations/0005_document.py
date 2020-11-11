# Generated by Django 3.1.2 on 2020-11-10 23:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('datapipeline', '0004_delete_document'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uploadedFile', models.FileField(upload_to='uploaded_csvs')),
                ('filename', models.CharField(max_length=250)),
            ],
        ),
    ]
