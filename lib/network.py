"""Handle networks as specified in the configuration."""
from lib.interface import Interface
from lib.log import debug, error, info
from modules import monitoring


class Network(object):
    """The Network class."""
    interfaces = []

    def __init__(self, ns, name, config):
        self.ns = ns
        self.name = name
        self.bridge = f'br-{name}'
        self.monitoring = config.monitoring
        for address, pairs in config.ports.items():
            for pair in pairs:
                for vlan_id, network_name in pair.items():
                    if name == network_name:
                        interface = Interface(address, vlan_id)
                        self.interfaces.append(interface)

    def init(self):
        """Initialize the network and its connected interfaces."""
        if not self.ns.exists():
            self.ns.add()

        self.ns.add_interface(self.name)
        # init bridge
        self.ns.execute(['brctl', 'addbr', self.bridge])
        self.ns.add_bridge_interface(self.bridge, self.name)
        self.ns.enable_interface(self.bridge)
        self.ns.enable_interface(self.name)

        for interface in self.interfaces:
            interface.init(self.ns)
            self.ns.add_bridge_interface(self.bridge, interface.linux_interface)
        info(f'Configured the following interfaces for network {self.name}',
             ', '.join([str(i) for i in self.interfaces]))


    def shutdown(self):
        """Shutdown the network and its connected interfaces."""
        for interface in self.interfaces:
            interface.shutdown(self.ns)
        self.ns.disable_interface(self.bridge)
        self.ns.execute(['brctl', 'delbr', self.bridge])
        self.ns.delete_interface(self.name)

        # if there is only the "lo" interface left in the namespace - remove it
        output = self.ns.execute(['ip', 'address', 'show']).decode('utf-8')
        if 'LOOPBACK' in output and len(output.splitlines()) == 2:
            debug('Namespace no longer needed -> remove it')
            self.ns.delete()

    def link_is_up(self):
        """Check the overall link status of connnected interfaces."""
        # Network status logic:
        # If all ports of a network are up -> up, otherwise -> down
        if self.monitoring == 'any':
            f = any
        else:
            f = all
        status = f([i.link_is_up(self.ns) for i in self.interfaces])
        return status
