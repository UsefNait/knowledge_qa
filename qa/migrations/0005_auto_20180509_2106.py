# Generated by Django 2.0.2 on 2018-05-09 20:06

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qa', '0004_auto_20180509_2024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='question_text',
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
    ]
