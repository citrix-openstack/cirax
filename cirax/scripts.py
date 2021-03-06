import logging
import argparse
import os
import sys
from collections import namedtuple

from novaclient import auth_plugin
from novaclient.v1_1 import client


ENV_MAPPING = {
    'OS_USERNAME': 'username',
    'OS_PASSWORD': 'password',
    'OS_TENANT_NAME': 'tenant',
    'OS_AUTH_URL': 'auth_url',
    'OS_AUTH_SYSTEM': 'auth_system',
    'OS_REGION_NAME': 'region_name',
}

RaxEnv = namedtuple('RaxEnv', ENV_MAPPING.values())


def parse_env(environ):
    return dict(
        (local_var, environ.get(env_var))
        for env_var, local_var in ENV_MAPPING.items())


def get_client(environ):
    rax_env = RaxEnv(**parse_env(environ))

    return client.Client(
        rax_env.username,
        rax_env.password,
        rax_env.tenant,
        rax_env.auth_url,
        auth_plugin=auth_plugin.load_plugin(rax_env.auth_system),
        region_name=rax_env.region_name)


def get_missing_env_vars(environ):
    missing_env_vars = []
    for env_name, _local_name in ENV_MAPPING.items():
        if environ.get(env_name) is None:
            missing_env_vars.append(env_name)
    return missing_env_vars


def configure_logging():
    logging.basicConfig(level=logging.INFO)


def env_vars_or_die():
    missing_env_vars = get_missing_env_vars(os.environ)
    if missing_env_vars:
        for varname in missing_env_vars:
            sys.stdout.write('environment variable %s is not set\n' % varname)
        sys.exit(1)
    return os.environ


def args_or_die():
    parser = argparse.ArgumentParser(description='List, and optionally '
                                                 'Cleanup cloud resources')
    parser.add_argument('--remove', help='Delete resources',
                        action='store_true')
    args = parser.parse_args()
    args.images = True
    args.servers = True
    args.keypairs = True
    return args


def generic_args_or_die():
    parser = argparse.ArgumentParser(description='List, and optionally '
                                                 'Cleanup cloud resources')
    parser.add_argument('startswith', help='A prefix to select resources')
    parser.add_argument('--remove', help='Delete resources',
                        action='store_true')
    parser.add_argument('--images', help='Deal with images', action='store_true')
    parser.add_argument('--servers', help='Deal with servers', action='store_true')
    parser.add_argument('--keypairs', help='Deal with keypairs', action='store_true')
    return parser.parse_args()


def create_resource_selector(startpattern):
    def resource_selector(resource):
        return resource.name.startswith(startpattern)

    return resource_selector


def generic_cleanup():
    configure_logging()
    args = generic_args_or_die()
    environ = env_vars_or_die()
    client = get_client(environ)
    cleanup(create_resource_selector(args.startswith), args, client)


def cleanup(resource_selector, args, client):
    logger = logging.getLogger(__name__ + '.cleanup')
    leftover_resources = []

    if args.keypairs:
        for keypair in client.keypairs.list():
            if resource_selector(keypair):
                logger.info('found keypair: %s', keypair.name)
                leftover_resources.append(keypair)

    if args.servers:
        for server in client.servers.list():
            if resource_selector(server):
                logger.info('found server: %s', server.name)
                leftover_resources.append(server)

    if args.images:
        for image in client.images.list():
            if resource_selector(image):
                logger.info('found image: %s', image.name)
                leftover_resources.append(image)


    if args.remove:
        for resource in leftover_resources:
            logger.info('deleting %s', resource.name)
            resource.delete()
