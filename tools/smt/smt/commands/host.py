from smt.commands import BaseCommand
from smt.common import get_instances


class Command(BaseCommand):

    help = 'manage hosts'

    def register(self, parser):

        parser.set_defaults(handle=self.do_list)

        subparsers = parser.add_subparsers()

        # Host list
        parser_list = subparsers.add_parser('list', help='list instances')
        parser_list.set_defaults(handle=self.do_list)

        parser_list.add_argument('-t', '--target',
                                 help='set target (local, pro)',
                                 dest='target',
                                 action='store',
                                 default='local')

        parser_list.add_argument('-r', '--role',
                                 help='role of the host',
                                 dest='role',
                                 action='store',
                                 default=None)

    def do_list(self, args):
        def line(**kwargs):
            print '{host:<50}{name:<30}{role:<20}{target:<5}'.format(**kwargs)

        line(host='HOST', name='NAME', role='ROLE', target='TARGET')

        for i in get_instances(role=args.role, target=args.target):
            line(
                host=i.host[:45] + '...' if len(i.host) > 45 else i.host,
                name=i.name[:28] or '---',
                role=i.role[:18] or '---',
                target=i.target[:5] or '---'
            )
