"""Define command line arguments for the application."""
import argparse


def parse_arguments():
    """Get commandline arguments."""
    parser = argparse.ArgumentParser(
        description='Setup Linux bridges for a given SSR interface configuration.')
    parser.add_argument('--create-symlinks', action='store_true',
                        help='Create namespace script directory structure')
    parser.add_argument('--kni-interface',
                        help='Standard argument used by namespace scripts')
    parser.add_argument('--kni-gateway',
                        help='Standard argument used by namespace scripts')
    parser.add_argument('--mac-address',
                        help='Standard argument used by namespace scripts')
    parser.add_argument('--namespace',
                        help='Standard argument used by namespace scripts')
    parser.add_argument('module', nargs='?',
                        help='Select the module to be used')
    parser.add_argument('kni_interface', nargs='?',
                        help='Standard argument used by namespace scripts')
    parser.add_argument('namespace', nargs='?',
                        help='Standard argument used by namespace scripts')
    parser.add_argument('--version', action='version',
                        version='t128-ethernet-port-management 1.1')
    return parser.parse_args()
