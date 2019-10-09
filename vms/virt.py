import subprocess

import libvirt

from . import errors

VIR_DOMAIN_NOSTATE = 0  # no state
VIR_DOMAIN_RUNNING = 1  # the domain is running
VIR_DOMAIN_BLOCKED = 2  # the domain is blocked on resource
VIR_DOMAIN_PAUSED = 3  # the domain is paused by user
VIR_DOMAIN_SHUTDOWN = 4  # the domain is being shut down
VIR_DOMAIN_SHUTOFF = 5  # the domain is shut off
VIR_DOMAIN_CRASHED = 6  # the domain is crashed
VIR_DOMAIN_PMSUSPENDED = 7  # the domain is suspended by guest power management
VIR_DOMAIN_LAST = 8  # NB: this enum value will increase over time as new events are added to the libvirt API. It reflects the last state supported by this version of the libvirt API.
VIR_DOMAIN_HOST_DOWN = 9  # host connect failed
VIR_DOMAIN_MISS = 10  # vm miss

VM_STATE = {
    VIR_DOMAIN_NOSTATE: 'no state',
    VIR_DOMAIN_RUNNING: 'running',
    VIR_DOMAIN_BLOCKED: 'blocked',
    VIR_DOMAIN_PAUSED: 'paused',
    VIR_DOMAIN_SHUTDOWN: 'shut down',
    VIR_DOMAIN_SHUTOFF: 'shut off',
    VIR_DOMAIN_CRASHED: 'crashed',
    VIR_DOMAIN_PMSUSPENDED: 'suspended',
    VIR_DOMAIN_LAST: '',
    VIR_DOMAIN_HOST_DOWN: 'host connect failed',
    VIR_DOMAIN_MISS: 'miss',
}

class VirtAPI(object):
    '''
    libvirt api包装
    '''
    def _host_alive(self, host_ipv4:str, times=3):
        '''
        检测宿主机是否可访问

        :param host_ipv4: 宿主机IP
        :param times:
        :return:
            True    # 可访问
            False   # 不可
        '''
        cmd = f'fping {host_ipv4} -r {times}'
        res, info = subprocess.getstatusoutput(cmd)
        if res == 0:
            return True
        return False

    def _get_connection(self, host_ip:str):
        '''
        建立与宿主机的连接

        :param host_ip: 宿主机IP
        :return:
            success: libvirt.virConnect
            failed: raise VmError()

        :raise VmError()
        '''
        if host_ip:
            if not self._host_alive(host_ip):
                raise errors.VmError(code=errors.ERR_HOST_CONNECTION)
            name = f'qemu+ssh://{host_ip}/system'
        else:
            name = 'qemu:///system'

        try:
            return libvirt.open(name=name)
        except libvirt.libvirtError as e:
            raise errors.VmError(code=errors.ERR_HOST_CONNECTION, err=e)

    def define(self, host_ipv4:str, xml_desc:str):
        '''
        在宿主机上创建一个虚拟机

        :param host_ipv4: 宿主机ip
        :param xml_desc: 定义虚拟机的xml
        :return:
            success: libvirt.virDomain()
            failed: raise VmError()

        :raise VmError()
        '''
        conn = self._get_connection(host_ipv4)
        try:
            dom = conn.defineXML(xml_desc)
            return dom
        except libvirt.libvirtError as e:
            raise errors.VmError(code=errors.ERR_VM_DEFINE, err=e)

    def get_domain(self, host_ipv4:str, vm_uuid:str):
        '''
        获取虚拟机

        :param host_ipv4: 宿主机IP
        :param vm_uuid: 虚拟机uuid
        :return:
            success: libvirt.virDomain()
            failed: raise VmError()

        :raise VmError()
        '''
        conn = self._get_connection(host_ipv4)
        try:
            return conn.lookupByUUIDString(vm_uuid)
        except libvirt.libvirtError as e:
            raise errors.VmError(code=errors.ERR_VM_MISSING, err=e)

    def domain_exists(self, host_ipv4:str, vm_uuid:str):
        '''
        检测虚拟机是否已存在

        :param host_ipv4: 宿主机IP
        :param vm_uuid: 虚拟机uuid
        :return:
            True: 已存在
            False: 不存在

        :raise VmError()
        '''
        conn = self._get_connection(host_ipv4)
        try:
            for d in conn.listAllDomains():
                if d.UUIDString() == vm_uuid:
                    return True
            return False
        except libvirt.libvirtError as e:
            raise errors.VmError(err=e)

    def undefine(self, host_ipv4:str, vm_uuid:str):
        '''
        删除一个虚拟机

        :param host_ipv4: 宿主机IP
        :param vm_uuid: 虚拟机uuid
        :return:
            success: True
            failed: False

        :raise VmError()
        '''
        dom = self.get_domain(host_ipv4, vm_uuid)
        try:
            if dom.undefine() == 0:
                return True
            return False
        except libvirt.libvirtError as e:
            raise errors.VmError(msg='删除虚拟机失败', err=e)

    def domain_status(self, host_ipv4:str, vm_uuid:str):
        '''
        获取虚拟机的当前状态

        :param host_ipv4: 宿主机IP
        :param vm_uuid: 虚拟机uuid
        :return:
            success: (state_code:int, state_str:str)

        :raise VmError()
        '''
        domain = self.get_domain(host_ipv4, vm_uuid)
        code = self._status_code(domain)
        state_str = VM_STATE.get(code, 'no state')
        return (code, state_str)

    def _status_code(self, domain:libvirt.virDomain):
        '''
        获取虚拟机的当前状态码

        :param domain: 虚拟机实例
        :return:
            success: state_code:int

        :raise VmError()
        '''
        try:
            info = domain.info()
            return info[0]
        except libvirt.libvirtError as e:
            raise errors.VmError(msg='获取虚拟机状态失败', err=e)

    def is_shutoff(self, host_ipv4:str, vm_uuid:str):
        '''
        虚拟机是否关机状态

        :param host_ipv4: 宿主机IP
        :param vm_uuid: 虚拟机uuid
        :return:
            True: 关机
            False: 未关机

        :raise VmError()
        '''
        domain = self.get_domain(host_ipv4=host_ipv4, vm_uuid=vm_uuid)
        return self._domain_is_shutoff(domain)

    def _domain_is_shutoff(self, domain:libvirt.virDomain):
        '''
        虚拟机是否关机状态

        :param domain: 虚拟机实例
        :return:
            True: 关机
            False: 未关机

        :raise VmError()
        '''
        code = self._status_code(domain)
        return code == VIR_DOMAIN_SHUTOFF

    def is_running(self, host_ipv4:str, vm_uuid:str):
        '''
        虚拟机是否开机状态，阻塞、暂停、挂起都属于开启状态

        :param host_ipv4: 宿主机IP
        :param vm_uuid: 虚拟机uuid
        :return:
            True: 开机
            False: 未开机

        :raise VmError()
        '''
        domain = self.get_domain(host_ipv4=host_ipv4, vm_uuid=vm_uuid)
        code = self._status_code(domain)
        if code in (VIR_DOMAIN_RUNNING, VIR_DOMAIN_BLOCKED, VIR_DOMAIN_PAUSED, VIR_DOMAIN_PMSUSPENDED):
            return True
        return False

    def _domain_is_running(self, domain:libvirt.virDomain):
        '''
        虚拟机是否开机状态，阻塞、暂停、挂起都属于开启状态

        :param domain: 虚拟机实例
        :return:
            True: 开机
            False: 未开机

        :raise VmError()
        '''
        code = self._status_code(domain)
        if code in (VIR_DOMAIN_RUNNING, VIR_DOMAIN_BLOCKED, VIR_DOMAIN_PAUSED, VIR_DOMAIN_PMSUSPENDED):
            return True
        return False

    def start(self, host_ipv4:str, vm_uuid:str):
        '''
        开机启动一个虚拟机

        :param host_ipv4: 虚拟机所在的宿主机ip
        :param vm_uuid: 虚拟机uuid
        :return:
            success: True
            failed: False

        :raise VmError()
        '''
        domain = self.get_domain(host_ipv4, vm_uuid)
        if self._domain_is_running(domain):
            return True

        try:
            res = domain.create()
            if res == 0:
                return True
            return False
        except libvirt.libvirtError as e:
            raise errors.VmError(msg='启动虚拟机失败', err=e)

    def reboot(self, host_ipv4:str, vm_uuid:str):
        '''
        重启虚拟机

        :param host_ipv4: 虚拟机所在的宿主机ip
        :param vm_uuid: 虚拟机uuid
        :return:
            success: True
            failed: False

        :raise VmError()
        '''
        domain = self.get_domain(host_ipv4, vm_uuid)
        if not self._domain_is_running(domain):
            return False

        try:
            res = domain.reboot()
            if res == 0:
                return True
            return False
        except libvirt.libvirtError as e:
            raise errors.VmError(msg='重启虚拟机失败', err=e)

    def shutdown(self, host_ipv4:str, vm_uuid:str):
        '''
        关机

        :param host_ipv4: 虚拟机所在的宿主机ip
        :param vm_uuid: 虚拟机uuid
        :return:
            success: True
            failed: False

        :raise VmError()
        '''
        domain = self.get_domain(host_ipv4, vm_uuid)
        if not self._domain_is_running(domain):
            return True

        try:
            res = domain.shutdown()
            if res == 0:
                return True
            return False
        except libvirt.libvirtError as e:
            raise errors.VmError(msg='关闭虚拟机失败', err=e)

    def poweroff(self, host_ipv4:str, vm_uuid:str):
        '''
        关闭电源

        :param host_ipv4: 虚拟机所在的宿主机ip
        :param vm_uuid: 虚拟机uuid
        :return:
            success: True
            failed: False

        :raise VmError()
        '''
        domain = self.get_domain(host_ipv4, vm_uuid)
        if not self._domain_is_running(domain):
            return True

        res = domain.destroy()
        try:
            if res == 0:
                return True
            return False
        except libvirt.libvirtError as e:
            raise errors.VmError(msg='关闭虚拟机电源失败', err=e)


    # def _xml_edit_vcpu(self, xml_desc, vcpu):
    #     xml = XMLEditor()
    #     xml.set_xml(xml_desc)
    #     root = xml.get_root()
    #     try:
    #         root.getElementsByTagName('vcpu')[0].firstChild.data = vcpu
    #     except:
    #         return False
    #     return root.toxml()
    #
    # def _xml_edit_mem(self, xml_desc, mem):
    #     xml = XMLEditor()
    #     xml.set_xml(xml_desc)
    #     try:
    #         node = xml.get_node(['memory'])
    #         if node:
    #             node.attributes['unit'].value = 'MiB'
    #             node.firstChild.data = mem
    #         node1 = xml.get_node(['currentMemory'])
    #         if node1:
    #             node1.attributes['unit'].value = 'MiB'
    #             node1.firstChild.data = mem
    #         return xml.get_root().toxml()
    #     except:
    #         return False



