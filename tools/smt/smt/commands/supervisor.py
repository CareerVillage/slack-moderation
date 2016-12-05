from fabric.api import sudo
from smt.commands import TargetRoleCommand


class Command(TargetRoleCommand):

    help = 'remote supervisor control'

    def register(self, parser):
        super(Command, self).register(parser)

        parser.add_argument('-a', '--action',
                            dest='action',
                            required=True,
                            help='action to perform (stop, start, reload)')

        parser.add_argument('-p', '--process',
                            dest='process',
                            help='process to perform action '
                                 '(optional for reload)')

    def apply(self, args):
        if args.process:
            sudo('supervisorctl {0} {1}'.format(args.action, args.process))
        else:
            sudo('supervisorctl {0}'.format(args.action))
