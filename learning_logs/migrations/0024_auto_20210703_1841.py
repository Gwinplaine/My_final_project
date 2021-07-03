# Generated by Django 3.2 on 2021-07-03 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_logs', '0023_alter_topic_topicimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='entryimage',
            field=models.ImageField(blank=True, default='images/entrydefault.jpg', null=True, upload_to='images'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='topicimage',
            field=models.ImageField(blank=True, default='images/topicdefault.jpg', null=True, upload_to='images'),
        ),
    ]
