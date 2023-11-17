"""Script to provide device-interface details."""
import json

from lib.namespace import Namespace
from lib.network import Network


def print_interface_details(details):
    """Return json structure for interface details."""
    print(json.dumps(details))


def run(args, config):
    """Entry point."""
    name = args.kni_interface
    ns = Namespace(args.namespace)
    network = Network(ns, name, config)
    link_status = {}
    for interface in network.interfaces:
        if interface.vlan_id:
            tagged = 'T'
        else:
            tagged = 'U'
        port = interface.port
        key = f'{tagged} {port.pci_address} ({port.linux_interface})'
        link_status[key] = '\tUP' if interface.link_is_up(ns) else '\tDOWN'

    print_interface_details({'Link status': link_status})
