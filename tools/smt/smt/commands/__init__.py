import functools
from fabric.api import env
from fabric.tasks import execute
from smt.common import get_instances


class BaseCommand(object):

    help = None

    def register(self, parser):
        pass


class TargetRoleCommand(BaseCommand):

    def __init__(self, allow_role=True, allow_target=True, allow_host=True,
                 role=None, target='local', host=None):
        self.allow_role = allow_role
        self.role = role
        self.allow_target = allow_target
        self.target = target
        self.allow_host = allow_host
        self.host = host

    def register(self, parser):

        parser.set_defaults(handle=self.do)

        if self.allow_role:
            parser.add_argument('-r', '--role',
                                dest='role',
                                required=True,
                                default=self.role,
                                help='role of the host')

        if self.allow_target:
            parser.add_argument('-t', '--target',
                                help='set target (local, pro)',
                                dest='target',
                                default=self.target)

        if self.allow_host:
            parser.add_argument('--host',
                                help='host wildcard',
                                dest='host',
                                default=self.host)

    def do(self, args):
        if not self.allow_role:
            args.role = self.role
        if not self.allow_target:
            args.target = self.target
        if not self.allow_host:
            args.host = self.host
        instances = get_instances(role=args.role, target=args.target)
        if args.host:
            instances = [i for i in instances if args.host in i.host]
        env.key_filename = [i.key for i in instances]
        f = functools.partial(self.apply, args)
        f.__name__ = self.__module__.split('.')[-1]
        execute(f, hosts=[i.host for i in instances])

    def apply(self, args):
        raise NotImplementedError
