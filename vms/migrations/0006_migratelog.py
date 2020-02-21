# Generated by Django 2.2.10 on 2020-02-20 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vms', '0005_auto_20200109_0832'),
    ]

    operations = [
        migrations.CreateModel(
            name='MigrateLog',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('vm_uuid', models.CharField(max_length=36, verbose_name='虚拟机UUID')),
                ('src_host_id', models.IntegerField(verbose_name='源宿主机ID')),
                ('src_host_ipv4', models.GenericIPAddressField(verbose_name='源宿主机IP')),
                ('dst_host_id', models.IntegerField(verbose_name='目标宿主机ID')),
                ('dst_host_ipv4', models.GenericIPAddressField(verbose_name='目标宿主机IP')),
                ('migrate_time', models.DateTimeField(auto_now_add=True, verbose_name='迁移时间')),
                ('result', models.BooleanField(verbose_name='迁移结果(无错误)')),
                ('content', models.TextField(blank=True, null=True, verbose_name='文字记录')),
                ('src_undefined', models.BooleanField(default=False, verbose_name='已清理源云主机')),
            ],
            options={
                'verbose_name': '虚拟机迁移记录',
                'verbose_name_plural': '虚拟机迁移记录表',
                'ordering': ['-id'],
            },
        ),
    ]
