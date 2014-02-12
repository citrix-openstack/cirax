from setuptools import setup


setup(
    name='cirax',
    version='0.1dev',
    description='CI in RAX',
    packages=['cirax'],
    install_requires=['rackspace-novaclient'],
    entry_points = {
        'console_scripts': [
            'cirax-cleanup = cirax.scripts:jenkins_cleanup',
            'cirax-nodepool-cleanup = cirax.scripts:nodepool_cleanup',
            'cirax-generic-cleanup = cirax.scripts:generic_cleanup',
        ]
    }
)
