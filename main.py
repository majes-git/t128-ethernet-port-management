#!/usr/bin/env python3

from importlib import import_module
from os import mkdir, symlink
from os.path import basename, isdir, islink, join

from lib.arguments import parse_arguments
from lib.config import Config
from lib.log import debug, error, exception, set_debug


CONFIG = '/etc/128technology/t128-ethernet-port-management.yaml'
BASE_DIR = '/etc/128technology/plugins/network-scripts/host'
LINK_PATH = '/usr/local/sbin/t128-ethernet-port-management.sh'
MODULES = [
    'init',
    'reinit',
    'startup',
    'state',
    'shutdown',
    'monitoring',
]


def create_symlinks(config):
    """Read config and create one folder per network-interface and symlinks."""
    for network in config.networks:
        dirname = join(BASE_DIR, network)
        if not isdir(dirname):
            debug('Creating directory:', dirname)
            mkdir(dirname)
        for module in MODULES:
            linkname = join(dirname, module)
            if not islink(linkname):
                debug('Creating symlink:', linkname)
                symlink(LINK_PATH, linkname)


def main():
    """The entrypoint."""
    try:
        # global catch all to logfile since there is not stderr by design
        args = parse_arguments()
        config = Config(CONFIG)
        if config.debug:
            set_debug()

        if args.create_symlinks:
            create_symlinks(config)
        else:
            # run a module from module folder if process name is a valid module
            module_name = basename(args.module)
            if module_name in MODULES:
                if module_name == 'reinit':
                    # for this use case reinit is the same like init
                    module_name = 'init'
                module = import_module(f'modules.{module_name}')
                module.run(args, config)
            else:
                error(f'Module {module_name} could not be found!')
    except Exception as e:
        exception(e)


if __name__ == '__main__':
    main()
