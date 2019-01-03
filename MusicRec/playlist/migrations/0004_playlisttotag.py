# Generated by Django 2.1 on 2018-12-27 02:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playlist', '0003_auto_20181227_0955'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlayListToTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pl_id', models.CharField(blank=True, max_length=64, verbose_name='歌单ID')),
                ('tag', models.CharField(blank=True, max_length=64, verbose_name='歌单标签')),
            ],
            options={
                'verbose_name_plural': '歌单标签',
                'db_table': 'playListToTag',
            },
        ),
    ]
