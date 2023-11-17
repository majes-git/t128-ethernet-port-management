"""Provide methods for network interface handling."""
from subprocess import run, DEVNULL, PIPE

from lib.log import debug, error


def get_interface_symlinks(prefix=''):
    """Call readlink on sysfs for network class."""
    command = f"{prefix} sh -c 'readlink /sys/class/net/*'"
    output = run(command, shell=True, encoding='utf-8',
                 stdout=PIPE, stderr=DEVNULL).stdout
    return output


def parse_output(output):
    """Extract pci addresses and linux interface names from sysfs."""
    ports = {}
    for line in output.splitlines():
        if 'pci' in line:
            content = line.split('pci')[1].split('/')
            address = content[-3]
            if address.startswith('virtio'):
                address = content[-4]
            linux_interface = content[-1]
            ports[address] = linux_interface
    return ports


def get_port_mappings():
    """Return dict with pci addresses and linux interface names."""
    ports = {}
    ports.update(parse_output(get_interface_symlinks()))
    prefix = 'ip netns exec t128-ethernet-port-management'
    ports.update(parse_output(get_interface_symlinks(prefix)))
    return ports


class Port(object):
    """The Port class."""

    def __init__(self, pci_address):
        # A port is a representation of the physical network connection.
        # It is identified by it's pci address and translates into a
        # linux (base) interface, like "eth0"
        self.pci_address = pci_address
        ports = get_port_mappings()
        try:
            self.linux_interface = ports[pci_address]
        except:
            error('Cannot find linux interface for:', pci_address)
            raise


class Interface(object):
    """The Interface class."""
    vlan_id = 0   # The default vlan-id to indicate there is no tagging

    def __init__(self, address, vlan_id=0):
        # An interface consists of a port and a vlan-id (default: 0)
        self.port = Port(address)
        self.linux_interface = self.port.linux_interface
        if vlan_id:
            self.set_vlan_id(vlan_id)
            self.linux_interface = f'{self.linux_interface}.{self.vlan_id}'

    def __repr__(self):
        if self.vlan_id:
            return f'{self.port.linux_interface}.{self.vlan_id}'
        return self.port.linux_interface

    def set_vlan_id(self, vlan_id):
        """Validate the provided VLAN ID."""
        try:
            vlan_id = int(vlan_id)
            if not (vlan_id > 0 and vlan_id < 4095):
                raise ValueError()
        except ValueError:
            error('Provided VLAN ID is not valid:', vlan_id)
        self.vlan_id = vlan_id

    def init(self, ns):
        """Initialize the interface."""
        ns.add_interface(self.port.linux_interface)
        ns.enable_interface(self.port.linux_interface)
        if self.vlan_id:
            ns.execute(['ip', 'link', 'add', 'link', self.port.linux_interface,
                        'name', self.linux_interface,
                        'type', 'vlan', 'id', str(self.vlan_id)])
            ns.enable_interface(self.linux_interface)

    def shutdown(self, ns):
        """Shutdown the interface."""
        if self.vlan_id:
            ns.execute(['ip', 'link', 'delete', self.linux_interface])
            output = ns.execute(['ip', 'link', 'show', 'type', 'vlan']).decode('utf-8')
            if f'@{self.port.linux_interface}' in output:
                # base interface still in use by other networks
                return
            debug(f'Disabling/deleting base interface {self.port.linux_interface}')
        ns.disable_interface(self.port.linux_interface)
        ns.delete_interface(self.port.linux_interface)

    def link_is_up(self, ns):
        """Check the link status of the interface."""
        output = ns.execute(['ethtool', self.port.linux_interface], show_debug=False)
        if output:
            return 'Link detected: yes' in output.decode('utf-8')
        return False
