# Generated by Django 2.0.2 on 2018-05-10 00:28

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qa', '0009_auto_20180510_0125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='answer_text',
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
    ]
