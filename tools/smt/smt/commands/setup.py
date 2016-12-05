import os
from datetime import datetime
from fabric.api import run, sudo, env, put, local
from fabric.tasks import execute
from smt.commands import BaseCommand
from smt.common import get_instances, get_setting, get_settings


class Command(BaseCommand):

    help = 'setup a node'

    def register(self, parser):

        parser.set_defaults(handle=self.__class__.do)

        parser.add_argument('-r', '--role',
                            dest='role',
                            required=False,
                            default='master',
                            help='role of the host')

        parser.add_argument('-t', '--target',
                            help='set target (local, pro)',
                            dest='target',
                            default='local')

        parser.add_argument('-e', '--reset-db',
                            help='run reset_db in the host (only for master)',
                            dest='reset_db',
                            action='store_true',
                            default=False)

        parser.add_argument('--host',
                            help='set host',
                            dest='host',
                            default=None)

        parser.add_argument('-m', '--manifest',
                            help='set manifest',
                            dest='manifest',
                            default=None)

    @staticmethod
    def do(args):
        target = args.target
        role = args.role
        manifest = args.manifest
        instances = get_instances(role=role, target=target)

        # Open the deploy log and append the current time
        with open('../deploys.log', 'a') as f:
            now = datetime.now().isoformat()
            f.write('{} - moderation {} ({})\n'.format(now, target, role))
            f.close()

        if args.host:
            instances = [i for i in instances if args.host in i.host]

        env.key_filename = [i.key for i in instances]

        print env.key_filename

        # Set the setup name
        setup_name = 'setup-{target}-{role}'.format(target=target, role=role)

        def get_instance(host):
            for instance in instances:
                if host == instance.host:
                    return instance
            return None

        try:
            # Execute the create tar command for the setup directory
            tar_command = ('tar cf {setup_name}.tar  '
                           '--exclude=.git -C {setup_dir} .')
            local(tar_command.format(setup_name=setup_name,
                                     setup_dir=get_setting('SETUP_DIR')))

            # Execute the create tar command for the target keys
            tar_command = ('tar rf {setup_name}.tar -C {path} '
                           'moderation_{target}_git_key '
                           'moderation_{target}_git_pub '
                           'moderation_{target}_ssl_key '
                           'moderation_{target}_ssl_crt')
            local(tar_command.format(path=get_setting('KEY_DIR'),
                                     setup_name=setup_name, target=target))

            # Execute the gzip command for the setup directory
            local('gzip {setup_name}.tar'.format(setup_name=setup_name))

            def puppet_apply():

                print env.host_string

                instance = get_instance(env.host_string)

                assert instance is not None, \
                    '{} instance not found'.format(env.host_string)

                # Get the target manifest file
                manifest_file = os.path.join(
                    get_setting('SETUP_DIR'), '{manifest}.pp') \
                    .format(manifest=manifest or instance.manifest)

                # Check if the target manifest file does exist
                if not os.path.isfile(os.path.abspath(manifest_file)):
                    print 'No manifest found: {manifest}.pp'.format(
                        manifest=manifest or instance.manifest
                    )
                    return

                # Upload the setup tar.gz file
                tar_gz = '{setup_name}.tar.gz'.format(setup_name=setup_name)
                put(tar_gz, tar_gz)

                # Decompress the uploaded file
                run('tar xzf {setup_name}.tar.gz'.format(
                    setup_name=setup_name
                ))

                # Move the uploaded keys to the temp directory
                str_command = 'mv moderation_{target}_git_key ' \
                              '/tmp/moderation_git_key'
                sudo(str_command.format(
                    target=target
                ))
                str_command = 'mv moderation_{target}_git_pub ' \
                              '/tmp/moderation_git_pub'
                sudo(str_command.format(
                    target=target
                ))

                str_command = 'mv moderation_{target}_ssl_key ' \
                              '/tmp/moderation_ssl_key'
                sudo(str_command.format(
                    target=target
                ))

                str_command = 'mv moderation_{target}_ssl_crt ' \
                              '/tmp/moderation_ssl_crt'
                sudo(str_command.format(
                    target=target
                ))

                # Run this before installing puppet and git
                sudo('apt-get update')
                sudo('apt-get install puppet git -y')

                def convert(val):
                    # TODO: Add support to other py types
                    if val is None:
                        val = '__NONE__'
                    elif val == '':
                        val = '__EMPTY__'
                    elif not isinstance(val, basestring):
                        val = str(val)

                    return '"{value}"'.format(
                        value=val.replace('\"', '\\\"')
                    )

                # Export variable function
                def export_variable(var_name, var_value):
                    return 'export FACTER_moderation_{name}={value};'.format(
                        name=var_name.lower(), value=convert(var_value))

                # Get the settings for the current target
                sets = get_settings('{target}_PUPPET'.format(target=target))

                # Export every variable on the settings
                facts = [export_variable(name, value)
                         for name, value in sets.items()]

                # Export the current target to the system variables
                facts.append(
                    'export FACTER_moderation_target=\'{target}\';'.format(
                        target=target)
                )

                # Export the reset_db flag to the system variables
                facts.append(
                    'export FACTER_moderation_reset_db=\'{b}\';'.format(
                        b=str(args.reset_db).lower())
                )

                # Set the puppet apply command
                puppet_command = ('{facts} puppet apply --modulepath=modules '
                                  '{manifest}.pp').format(
                                      facts=''.join(facts),
                                      manifest=manifest or instance.manifest)

                # Run the puppet apply command
                sudo(puppet_command)

            execute(puppet_apply, hosts=[i.host for i in instances])

        except Exception, e:
            import traceback
            print traceback.format_exc()
            print '[Error]', e

        finally:
            setup_name = {'setup_name': setup_name}

            if os.path.isfile('{setup_name}.tar.gz'.format(**setup_name)):
                local('rm {setup_name}.tar.gz'.format(**setup_name))

            if os.path.isfile('{setup_name}.tar'.format(**setup_name)):
                local('rm {setup_name}.tar'.format(**setup_name))
