# Generated by Django 4.2.4 on 2024-10-21 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0012_remove_article_transcript_article_subtitles'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='transcript',
            field=models.TextField(blank=True, null=True),
        ),
    ]
