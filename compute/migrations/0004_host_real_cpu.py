# Generated by Django 2.2.8 on 2019-12-25 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compute', '0003_auto_20191101_1024'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='real_cpu',
            field=models.IntegerField(default=20, verbose_name='真实物理CPU总数'),
        ),
    ]
