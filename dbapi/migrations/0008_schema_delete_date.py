# Generated by Django 2.2 on 2020-09-05 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbapi', '0007_students'),
    ]

    operations = [
        migrations.AddField(
            model_name='schema',
            name='delete_date',
            field=models.DateTimeField(help_text='逻辑表删除时间', null=True),
        ),
    ]
