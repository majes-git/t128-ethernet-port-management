"""Script to monitor network namespace/host interface."""
from lib.namespace import Namespace
from lib.network import Network

def run(args, config):
    """Entry point."""
    name = args.kni_interface
    ns = Namespace(args.namespace)
    network = Network(ns, name, config)
    if network.link_is_up():
        print('up')
    else:
        print('down')
