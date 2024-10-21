# Generated by Django 4.2.4 on 2024-10-21 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0014_alter_article_subtitles'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoTranscript',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('youtube_url', models.URLField(max_length=255, unique=True)),
                ('transcript', models.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='article',
            name='transcript',
        ),
    ]