# Generated by Django 3.1.2 on 2020-12-06 19:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datapipeline', '0010_attribute_datacategory_datacategorystudyxref_study_studygroup_subject'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datacategorystudyxref',
            name='data_category_id',
        ),
        migrations.RemoveField(
            model_name='datacategorystudyxref',
            name='study_id',
        ),
        migrations.RemoveField(
            model_name='studygroup',
            name='study_id',
        ),
        migrations.RemoveField(
            model_name='subject',
            name='study_group_id',
        ),
        migrations.DeleteModel(
            name='Attribute',
        ),
        migrations.DeleteModel(
            name='DataCategory',
        ),
        migrations.DeleteModel(
            name='DataCategoryStudyXref',
        ),
        migrations.DeleteModel(
            name='Study',
        ),
        migrations.DeleteModel(
            name='StudyGroup',
        ),
        migrations.DeleteModel(
            name='Subject',
        ),
    ]
