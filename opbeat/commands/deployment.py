from opbeat.command import CommandBase
from opbeat.runner import build_client
from opbeat.conf import defaults
from opbeat.conf.defaults import CLIENT_ID

import pkg_resources
from pip.vcs import vcs
from pip.util import get_installed_distributions

import argparse
import sys
import os
import socket

VCS_NAME_MAP = {
	'git': 'git',
	'hg': 'mercurial',
	'svn': 'subversion'
}

SERVER_NAME = socket.gethostname()


_VERSION_CACHE = {}

def get_versions_from_installed(module_list=None):
	if not module_list:
		return {}

	ext_module_list = set()
	for m in module_list:
		parts = m.split('.')
		ext_module_list.update('.'.join(parts[:idx]) for idx in xrange(1, len(parts) + 1))

	versions = {}
	for module_name in ext_module_list:
		if module_name not in _VERSION_CACHE:
			try:
				__import__(module_name)
			except ImportError:
				continue
			app = sys.modules[module_name]
			if hasattr(app, 'get_version'):
				get_version = app.get_version
				if callable(get_version):
					version = get_version()
				else:
					version = get_version
			elif hasattr(app, 'VERSION'):
				version = app.VERSION
			elif hasattr(app, '__version__'):
				version = app.__version__
			elif pkg_resources:
				# pull version from pkg_resources if distro exists
				try:
					version = pkg_resources.get_distribution(module_name).version
				except pkg_resources.DistributionNotFound:
					version = None
			else:
				version = None

			if isinstance(version, (list, tuple)):
				version = '.'.join(str(o) for o in version)
			_VERSION_CACHE[module_name] = version
		else:
			version = _VERSION_CACHE[module_name]
		if version is None:
			continue
		versions[module_name] = version

	return versions


def get_version_from_distributions(distributions, logger):
	result = {}
	for d in distributions:
		result[d.key] = {'module': d.key}

		if d.has_version():
			result[d.key]['version'] = d.version

		vcs_version = get_version_from_location(d.location, logger)
		if vcs_version:
			result[d.key]['vcs'] = vcs_version

	return result

# Recursively try to find vcs.
def get_version_from_location(location, logger):
	backend_cls = vcs.get_backend_from_location(location)
	if backend_cls:
		backend = backend_cls()
		url, rev = backend.get_info(location)

		# Mercurial sometimes returns something like
		# "Not trusting file /home/alice/repo/.hg/hgrc from untrusted user alice, group users"
		# We'll ignore it for now
		if len(url) > 250 or len(rev) > 100:
			return None

		url = annotate_url_with_ssh_config_info(url, logger)

		vcs_type = VCS_NAME_MAP[backend_cls.name]

		return {'type': vcs_type,'revision':rev, 'repository':url}
	else:
		head, tail = os.path.split(location)
		if head and head != '/': ## TODO: Support windows
			return get_version_from_location(head, logger)
		else:
			return None

def get_repository_info(logger, directory=None):
	if not directory:
		directory = os.getcwd()
	cwd_rev_info = get_version_from_location(directory, logger)
	return cwd_rev_info

def extract_host_from_netloc(netloc):
	if '@' in netloc:
		_, netloc = netloc.split('@')

	if ':' in netloc:
		host, _ = netloc.split(':')
	else:
		host = netloc

	return host


def get_ssh_config(logger):
	try:
		from ssh.config import SSHConfig
	except:
		return None
	from os.path import expanduser

	try:
		config_file = file(expanduser('~/.ssh/config'))
	except IOError, ex:
		logger.debug(ex)
		return None
	else:
		try:
			config = SSHConfig()
			config.parse(config_file)
		except Exception, ex:
			logger.debug(ex)
			return None
	return config

def annotate_url_with_ssh_config_info(url, logger):
	from urlparse import urlsplit, urlunsplit

	config = get_ssh_config(logger)

	added = None
	if config:
		parsed_url = urlsplit(url)
		if not parsed_url.hostname:
			# schema missing
			added = "git://"
			parsed_url = urlsplit(added + url)

		parsed_asdict = parsed_url._asdict()

		host = extract_host_from_netloc(parsed_url.netloc)

		hive = config.lookup(host)
		if 'hostname' in hive:
			netloc = parsed_url.netloc.replace(host, hive['hostname'])

		parsed_asdict['path'] = parsed_url.path
		parsed_asdict['netloc'] = netloc

		url = urlunsplit(parsed_asdict.values())
		if added and url.startswith(added):
			return url[len(added):]
		else:
			return url
	return url


def send_deployment_info(client, logger, include_paths = None, directory=None, module_name = '_repository'):
	if include_paths:
		versions = get_versions_from_installed(include_paths)
		versions = dict([(module, {'module':module, 'version':version}) for module, version in versions.items()])
	else:
		versions = {}

	dist_versions = get_version_from_distributions(get_installed_distributions(), logger)
	versions.update(dist_versions)

	rep_info = get_repository_info(logger, directory)

	if rep_info:
		versions[module_name] = {'module':module_name, 'vcs':rep_info}

	# Versions are returned as a dict of "module":"version"
	# We convert it here. Just ditch the keys.
	list_versions = [v for k,v in versions.items()]

	server_name = SERVER_NAME

	data = {'server_name':server_name, 'releases':list_versions}

	url = client.server+(defaults.DEPLOYMENT_API_PATH.format(client.project_id))
	
	return client.send(url=url,data=data)


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
			'-p', '--project-id',
			help='Use this project id. Can be set with environment  \
variable OPBEAT_PROJECT_ID',
			dest="project_id",
			required=True,
			default=os.environ.get('OPBEAT_PROJECT_ID')
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
			help='Use this as the module name.',
			default="_repository")

		self.parser.add_argument(
			'--dry-run',
			help="Don't send anything.  \
Use '--verbose' to print the request instead.",
			action="store_true",
			dest="dry_run")

		self.parser.add_argument('--client-id',
			help="Override OAuth client id (you probably don't need this)",
			default=os.environ.get('OPBEAT_CLIENT_ID', CLIENT_ID)
			)

	def run(self, args):
		client = build_client(
			project_id = args.project_id,
			server = args.server,
			logger = self.logger,
			access_token = args.access_token,
			config_file=args.config_file,
			client_id = args.client_id,
			dry_run = args.dry_run
			)
		if not client: return
		self.logger.info('Sending deployment info...')
		self.logger.info("Using directory: %s", args.directory)

		send_deployment_info(client, self.logger, args.include_paths, args.directory, args.module_name)

command = DeploymentCommand

