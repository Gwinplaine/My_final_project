# Generated by Django 3.2 on 2021-07-03 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20210703_2011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogentry',
            name='blogtitle',
            field=models.CharField(max_length=150),
        ),
    ]
