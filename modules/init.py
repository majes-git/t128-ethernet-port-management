"""Script to initialize network namespace for host interface."""
from lib.log import info
from lib.namespace import Namespace
from lib.network import Network


def run(args, config):
    """Entry point."""
    name = args.kni_interface
    info('Initializing network', name)
    ns = Namespace(args.namespace)
    network = Network(ns, name, config)
    network.init()
