from rest_framework import serializers

from vms.models import Vm
from compute.models import Center, Group, Host
from network.models import Vlan
from image.models import Image
from vdisk.models import Vdisk


class VmSerializer(serializers.ModelSerializer):
    '''
    虚拟机序列化器
    '''
    user = serializers.SerializerMethodField() # 自定义user字段内容
    create_time = serializers.SerializerMethodField()  # 自定义字段内容
    host = serializers.SerializerMethodField()
    mac_ip = serializers.SerializerMethodField()
    uuid = serializers.SerializerMethodField()

    class Meta:
        model = Vm
        fields = ('uuid', 'name', 'vcpu', 'mem', 'disk', 'host', 'mac_ip', 'user', 'create_time')
        # depth = 1

    def get_uuid(self, obj):
        return obj.get_uuid()

    def get_user(selfself, obj):
        return {'id': obj.user.id, 'username': obj.user.username}

    def get_create_time(self, obj):
        if not obj.create_time:
            return ''
        return obj.create_time.strftime('%Y-%m-%d %H:%M:%S')

    def get_host(self, obj):
        return obj.host.ipv4

    def get_mac_ip(self, obj):
        return obj.mac_ip.ipv4


class VmCreateSerializer(serializers.Serializer):
    '''
    创建虚拟机序列化器
    '''
    image_id = serializers.IntegerField(label='镜像id', required=True, min_value=1, help_text='系统镜像id')
    vcpu = serializers.IntegerField(label='cpu数', required=True, min_value=1, help_text='cpu数')
    mem = serializers.IntegerField(label='内存大小', required=True, min_value=200)
    vlan_id = serializers.IntegerField(label='子网id', required=True, min_value=1, help_text='子网id')
    group_id = serializers.IntegerField(label='宿主机组id', required=False, allow_null=True, min_value=1, help_text='宿主机组id', default=None)
    host_id = serializers.IntegerField(label='宿主机id', required=False, allow_null=True, min_value=1, help_text='宿主机id', default=None)
    remarks = serializers.CharField(label='备注', required=False, allow_blank=True, max_length=255, default='')

    def validate(self, data):
        group_id = data.get('group_id')
        host_id = data.get('host_id')

        if not group_id and not host_id:
            raise serializers.ValidationError(detail={'code_text': 'group_id和host_id参数必须提交其中一个'})
        return data


class VmPatchSerializer(serializers.Serializer):
    '''
    创建虚拟机序列化器
    '''
    vcpu = serializers.IntegerField(label='cpu数', required=False, min_value=1, help_text='cpu数')
    mem = serializers.IntegerField(label='内存大小', required=False, min_value=200)

    def validate(self, data):
        return data


class CenterSerializer(serializers.ModelSerializer):
    '''
    分中心序列化器
    '''
    class Meta:
        model = Center
        fields = ('id', 'name', 'location', 'desc')


class GroupSerializer(serializers.ModelSerializer):
    '''
    宿主机组序列化器
    '''
    class Meta:
        model = Group
        fields = ('id', 'name', 'center', 'desc')


class HostSerializer(serializers.ModelSerializer):
    '''
    宿主机序列化器
    '''
    class Meta:
        model = Host
        fields = ('id', 'ipv4', 'group', 'vlans', 'vcpu_total', 'vcpu_allocated', 'mem_total', 'mem_allocated',
                  'mem_reserved', 'vm_limit', 'vm_created', 'enable', 'desc')


class VlanSerializer(serializers.ModelSerializer):
    '''
    子网网段序列化器
    '''
    class Meta:
        model = Vlan
        fields = ('id', 'name', 'br', 'net_type', 'enable', 'subnet_ip', 'net_mask', 'gateway', 'dns_server', 'remarks')


class ImageSerializer(serializers.ModelSerializer):
    '''
    子网网段序列化器
    '''
    class Meta:
        model = Image
        fields = ('id', 'name', 'version', 'type', 'enable', 'ceph_pool', 'base_image', 'snap', 'xml_tpl', 'create_time', 'desc')


class AuthTokenDumpSerializer(serializers.Serializer):
    key = serializers.CharField()
    user = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()

    def get_user(self, obj):
        return obj.user.username

    def get_created(self, obj):
        return obj.created.strftime('%Y-%m-%d %H:%M:%S')


class VdiskSerializer(serializers.ModelSerializer):
    '''
    虚拟硬盘序列化器
    '''
    group = serializers.SerializerMethodField()
    quota = serializers.SerializerMethodField()
    class Meta:
        model = Vdisk
        fields = ('uuid', 'size', 'vm', 'user', 'quota', 'create_time', 'attach_time', 'enable', 'remarks', 'group')
        depth = 0

    def get_group(self, obj):
        return obj.quota.group.name

    def get_quota(self, obj):
        return obj.quota.name


class VdiskCreateSerializer(serializers.Serializer):
    '''
    虚拟硬盘创建序列化器
    '''
    size = serializers.IntegerField(label='容量大小（GB）', required=True, min_value=1, help_text='容量大小,单位GB')
    quota_id = serializers.IntegerField(label='硬盘存储池id', required=False, allow_null=True, min_value=1, help_text='宿主机组id', default=None)
    group_id = serializers.IntegerField(label='宿主机组id', required=False, allow_null=True, min_value=1, help_text='宿主机组id', default=None)
    remarks = serializers.CharField(label='备注', required=False, default='')

    def validate(self, data):
        group_id = data.get('group_id')
        quota_id = data.get('quota_id')

        if not group_id and not quota_id:
            raise serializers.ValidationError(detail={'code_text': 'group_id和quota_id参数必须提交其中一个'})
        return data

