# Generated by Django 4.2.4 on 2024-10-21 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0011_hyperlink_article'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='transcript',
        ),
        migrations.AddField(
            model_name='article',
            name='subtitles',
            field=models.TextField(blank=True, null=True),
        ),
    ]
