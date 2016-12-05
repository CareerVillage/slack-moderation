import os
from smt.conf import settings


class VagrantInstance:

    def __init__(self, role, ip):
        self.target = 'local'
        self.role = role
        self.ip = ip

    @property
    def name(self):
        return 'local-{role}'.format(role=self.role)

    @property
    def host(self):
        return 'vagrant@{ip}:22'.format(ip=self.ip)

    @property
    def key(self):
        return '~/.vagrant.d/insecure_private_key'

    @property
    def manifest(self):
        return self.role


class EC2Instance:

    def __init__(self, instance):
        self.instance = instance

    @property
    def name(self):
        return self.instance.tags.get('Name')

    @property
    def target(self):
        return self.instance.tags.get('Target')

    @property
    def role(self):
        return self.instance.tags.get('Role')

    @property
    def host(self):
        return 'ubuntu@{ip}:22'.format(ip=self.instance.public_dns_name)

    @property
    def key(self):
        return os.path.join(settings.KEY_DIR, self.instance.key_name)

    @property
    def manifest(self):
        return self.role
