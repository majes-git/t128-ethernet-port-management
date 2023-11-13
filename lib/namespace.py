"""Provide Namespace environment"""
from subprocess import check_output, CalledProcessError, STDOUT

from lib.log import debug, error


class NamespaceException(Exception):
    """Helper exception for namespace related issues."""


class Namespace(object):
    """The Namespace class."""
    _IP_COMMAND = "/usr/sbin/ip"

    def __init__(self, namespace_name):
        try:
            self.name, self.id = namespace_name.split(':')
        except ValueError:
            error('Namespace string cannot be parsed:', namespace_name)

    def _exec(self, *args, raise_error=False, show_debug=True):
        output = ''
        try:
            command = [self._IP_COMMAND] + list(*args)
            if show_debug:
                debug('namespace.py _exec():', command)
            output = check_output(command, stderr=STDOUT)
            return output
        except CalledProcessError as e:
            if raise_error:
                error('Error during netns execution.',
                      'Command was: "{}".'.format(' '.join(e.cmd)),
                      'Output was:', e.output.decode('utf-8').strip())
                raise NamespaceException() from e

    def execute(self, command, show_debug=True):
        """Execute a command inside the network namespace."""
        return self._exec(['netns', 'exec', self.name, *command], show_debug=show_debug)

    def add(self):
        """Create network namespace."""
        self._exec(['netns', 'add', self.name])
        self._exec(['netns', 'set', self.name, self.id])

    def delete(self):
        """Delete network namespace."""
        return self._exec(['netns', 'delete', self.name])

    def exists(self):
        """Check if network namespace exists."""
        for line in self._exec(['netns', 'list']).splitlines():
            #debug('namespace.exists:', line)
            if self.name == line.decode('utf-8').split(' ')[0]:
                return True
            continue
        return False

    def add_interface(self, name):
        """Move an existing network interface into netns."""
        return self._exec(['link', 'set', name, 'netns', self.name])

    def delete_interface(self, name):
        """Move an existing network interface into netns."""
        return self.execute(['ip', 'link', 'set', name, 'netns', '1'])

    def add_bridge_interface(self, bridge, interface):
        """Move an existing network interface into netns."""
        return self.execute(['brctl', 'addif', bridge, interface])

    def enable_interface(self, interface):
        """Set interface inside the netns to UP."""
        return self.execute(['ip', 'link', 'set', 'up', 'dev', interface])

    def disable_interface(self, interface):
        """Set interface inside the netns to DOWN."""
        return self.execute(['ip', 'link', 'set', 'down', 'dev', interface])
