# Generated by Django 3.2 on 2021-07-01 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_logs', '0017_remove_topic_topicimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='topicimage',
            field=models.ImageField(blank=True, null=True, upload_to='images'),
        ),
    ]