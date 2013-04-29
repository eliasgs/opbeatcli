from opbeatcli.conf.defaults import CLIENT_ID
from opbeatcli.utils.ssh_config import SSHConfig
from opbeatcli.modprobes.release import Module, Vcs, Release

import pkg_resources
from pip.vcs import vcs
from pip.util import get_installed_distributions


import os
from os.path import expanduser

VCS_NAME_MAP = {
	'git': 'git',
	'hg': 'mercurial',
	'svn': 'subversion'
}


_VERSION_CACHE = {}


def get_versions_from_installed(module_list=None):
	if not module_list:
		return {}

	ext_module_list = set()
	for m in module_list:
		parts = m.split('.')
		ext_module_list.update(
			'.'.join(parts[:idx]) for idx in xrange(1, len(parts) + 1))

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
					version = pkg_resources.get_distribution(
						module_name).version
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
		result[d.key] = {'module': {'name': d.key}}

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

		if backend_cls.name not in VCS_NAME_MAP:
			return None

		vcs_type = VCS_NAME_MAP[backend_cls.name]

		return {'type': vcs_type, 'revision': rev, 'repository': url}
	else:
		head, tail = os.path.split(location)
		if head and head != '/':  # TODO: Support windows
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
			added = "http://"
			parsed_url = urlsplit(added + url)

		host = extract_host_from_netloc(parsed_url.netloc)

		hive = config.lookup(host)
		if 'hostname' in hive:
			netloc = parsed_url.netloc.replace(host, hive['hostname'])

		parsed = (
			parsed_url[0], netloc, parsed_url.path,
			parsed_url[3], parsed_url[4]
		)

		url = urlunsplit(parsed)
		if added and url.startswith(added):
			return url[len(added):]
		else:
			return url
	return url


def get_default_module_name(directory):
	if directory[-1:] == '/':
		return os.path.basename(directory[:-1])
	else:
		return os.path.basename(directory)

def run(logger, include_paths, directory, module_name):
	if include_paths:
		versions = get_versions_from_installed(include_paths)
		versions = dict([(module, {'module': {'name': module}, 'version':
						version}) for module, version in versions.items()])
	else:
		versions = {}

	dist_versions = get_version_from_distributions(
		get_installed_distributions(), logger)
	versions.update(dist_versions)

	rep_info = get_repository_info(logger, directory)

	if rep_info:
		if not module_name:
			module_name = get_default_module_name(directory)

		versions[module_name] = {'module': {'name': module_name}, 'vcs': rep_info}
	
	# Versions are returned as a dict of "module":"version"
	# We convert it here. Just ditch the keys.
	list_versions = [v for k, v in versions.items()]

	# Quick fix for the new modprobes structure	
	releases = []
	_vcs = None
	for ver in list_versions:
		mod = Module(ver['module']['name'])
		
		if (ver.get('vcs')):
			_vcs = Vcs(
				ver['vcs'].get('type'),
				ver['vcs'].get('revision'),
				ver['vcs'].get('repository'),
				ver['vcs'].get('branch'))
		releases.append(Release(mod, ver['version'], _vcs))

	return releases

