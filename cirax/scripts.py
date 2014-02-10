import logging
import argparse
from novaclient import auth_plugin
from novaclient.v1_1 import client
from collections import namedtuple
import os


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
    rax_env = RaxEnv(**parse_env(os.environ))

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


def is_jenkins_resource(resource):
    return resource.name.startswith('J')


def jenkins_cleanup():
    cleanup()


def cleanup():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__ + '.cleanup')
    parser = argparse.ArgumentParser(description='List, and optionally '
        'Cleanup cloud resources')
    parser.add_argument('--remove', help='Delete resources',
                        action='store_true')
    args = parser.parse_args()

    missing_env_vars = get_missing_env_vars(os.environ)
    client = get_client(os.environ)
    leftover_resources = []

    for keypair in client.keypairs.list():
        if is_jenkins_resource(keypair):
            logger.info('found keypair: %s', keypair.name)
            leftover_resources.append(keypair)

    for server in client.servers.list():
        if is_jenkins_resource(server):
            logger.info('found server: %s', server.name)
            leftover_resources.append(server)

    for image in client.images.list():
        if is_jenkins_resource(image):
            logger.info('found image: %s', image.name)
            leftover_resources.append(image)


    if args.remove:
        for resource in leftover_resources:
            logger.info('deleting %s', resource.name)
            resource.delete()
