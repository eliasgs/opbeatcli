from opbeatcli.command import CommandBase
from opbeatcli.runner import build_client
from opbeatcli.modprobes import probe

from opbeatcli.conf import defaults
import argparse
import sys
import socket

import os

def send_deployment_info(client, logger, hostname, include_paths=None, directory=None, module_name=None):

    releases = probe.all(logger, include_paths, directory, module_name)
    versions = []
    for rel in releases:
        version = {
            'module': {
                'name': rel.module.name,
                'type': rel.module.module_type}}

        if rel.version:
            version['version'] = rel.version
        if rel.vcs:
            version['vcs'] = {
                'type': rel.vcs.vcs_type,
                'revision': rel.vcs.revision,
                'repository': rel.vcs.repository,
                'branch': rel.vcs.branch}

        versions.append(version)

    data = {'machines': [{'hostname': hostname}], 'releases': versions}

    url = client.server + (defaults.DEPLOYMENT_API_PATH.format(client.organization_id, client.app_id))

    return client.send(url=url, data=data)


class ValidateDirectory(argparse.Action):
    def __call__(self, parser, args, values, option_string=None):
        directory = values

        if not os.path.isdir(directory):
            raise ValueError('Invalid directory {s!r}'.format(s=directory))
        setattr(args, 'directory', directory)


class DeploymentCommand(CommandBase):
    name = "deployment"
    description = "Sends deployment info ASAP."

    def add_args(self):
        super(DeploymentCommand, self).add_args()

        self.parser.add_argument(
            "--hostname", action="store", dest="hostname",
            help="Override hostname of current machine. Can be set with environment variable OPBEAT_HOSTNAME",
            default=os.environ.get('OPBEAT_HOSTNAME', defaults.HOSTNAME)
        )

        self.parser.add_argument(
            '-i', '--include-path',
            help='Search this directory.',
            dest="include_paths")
        self.parser.add_argument(
            '-d', '--directory',
            help='Take repository information from this directory.  \
Defaults to current working directory',
            dest="directory",
            default=os.getcwd(),
            action=ValidateDirectory)

        self.parser.add_argument(
            '-m', '--module-name',
            help='Use this as the module name.')

        self.parser.add_argument(
            '--dry-run',
            help="Don't send anything.  \
Use '--verbose' to print the request.",
            action="store_true",
            dest="dry_run")

    def run(self, args):
        client = build_client(
            organization_id=args.organization_id,
            app_id=args.app_id,
            server=args.server,
            logger=self.logger,
            secret_token=args.secret_token,
            dry_run=args.dry_run
        )
        if not client:
            return
        self.logger.info('Sending deployment info...')
        self.logger.info("Using directory: %s", args.directory)

        send_deployment_info(client, self.logger, args.hostname, args.include_paths,
                            args.directory, args.module_name)

command = DeploymentCommand
