from setuptools import setup


setup(
    name='cirax',
    version='0.1dev',
    description='CI in RAX',
    packages=['cirax'],
    install_requires=['rackspace-novaclient'],
    entry_points = {
        'console_scripts': [
            'cirax-cleanup = cirax.scripts:generic_cleanup',
        ]
    }
)
