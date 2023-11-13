"""Provide methods for config file handling."""
import yaml


class Config(object):
    """The application's configuration"""
    def __init__(self, filename):
        self.load_from_file(filename)
        self.init_ports()
        self.debug = bool(self.data.get('debug', False))

    def init_ports(self):
        """Initialize router ports based on configuration."""
        self.ports = {}
        self.networks = []
        for port in self.data.get('ports'):
            for address, networks in port.items():
                if isinstance(networks, str):
                    networks = [{0: networks}]
                self.ports[address] = networks

                # prepare a list of networks
                for network_pair in networks:
                    for network in network_pair.values():
                        if network not in self.networks:
                            self.networks.append(network)

    def load_from_file(self, filename):
        """Load configuration from file."""
        with open(filename, encoding='utf-8') as fd:
            self.data = yaml.safe_load(fd)
