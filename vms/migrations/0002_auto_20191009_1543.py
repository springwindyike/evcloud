# Generated by Django 2.2.6 on 2019-10-09 07:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vms', '0001_squashed_0002_auto_20191008_1635'),
    ]

    operations = [
        migrations.AddField(
            model_name='vm',
            name='image',
            field=models.ForeignKey(default=1, help_text='创建此虚拟机时使用的源系统镜像，disk从image复制', on_delete=django.db.models.deletion.CASCADE, to='vms.Image', verbose_name='源镜像'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='image',
            name='snap',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='当前生效镜像快照'),
        ),
        migrations.AlterField(
            model_name='macip',
            name='desc',
            field=models.TextField(blank=True, default='', verbose_name='备注说明'),
        ),
    ]
