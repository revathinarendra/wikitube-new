# Generated by Django 4.2.4 on 2024-09-24 15:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0004_article_contents'),
    ]

    operations = [
        migrations.RenameField(
            model_name='quiz',
            old_name='article_name',
            new_name='article',
        ),
        migrations.AddField(
            model_name='article',
            name='quiz',
            field=models.ManyToManyField(blank=True, related_name='article_quizzes', to='directory.quiz'),
        ),
        migrations.AddField(
            model_name='content',
            name='article',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='content_articles', to='directory.article'),
        ),
        migrations.AlterField(
            model_name='article',
            name='article_video_thumbnail',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='contents',
            field=models.ManyToManyField(blank=True, related_name='articles_contents', to='directory.content'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='correct_options',
            field=models.TextField(help_text='Enter the correct options separated by semicolon'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='opt_values',
            field=models.TextField(help_text='Enter the option values corresponding to each option, separated by semicolon'),
        ),
    ]