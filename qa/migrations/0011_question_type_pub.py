# Generated by Django 2.0.2 on 2018-05-13 00:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qa', '0010_auto_20180510_0128'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='type_pub',
            field=models.CharField(default='question', max_length=200),
        ),
    ]
