# Generated by Django 4.1.7 on 2023-04-25 05:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0006_post_edited_alter_user_followers_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='content',
            field=models.TextField(max_length=264),
        ),
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.TextField(max_length=264),
        ),
    ]
