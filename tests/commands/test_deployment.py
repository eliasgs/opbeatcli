import unittest
import mock
import os
import logging
import argparse


from datetime import datetime, timedelta

from opbeatcli.modprobes.pip_probe import (annotate_url_with_ssh_config_info, get_default_module_name)
from opbeatcli.commands.deployment import DeploymentCommand
from opbeatcli.client import Client

logger = logging.getLogger('opbeatcli.tests')

class MockSshConfig(object):
	def lookup(self, host):
		try:
			return {'opbeat_python':{'hostname':'github.com'}}[host]
		except:
			return {'hostname':host}


class FakeArgs(object):
	def __init__(self, **kwargs):
		for k, v in kwargs.items():
			setattr(self, k, v)

class TestRun(unittest.TestCase):
	@mock.patch("opbeatcli.runner.Client.send")
	def test_module_type(self, send):
		parser = argparse.ArgumentParser(description="Dummy parser")
		subparse = parser.add_subparsers()

		cmd = DeploymentCommand(subparse)

		args = FakeArgs(**{
			'organization_id': 'org_id',
			'app_id': 'app_id',
			'secret_token': 'token',
			'server': 'server',
			'dry_run': 'dry_run',
			'module_name': 'module_name',
			'directory': 'directory',
			'hostname': 'hostname',
			'include_paths': 'include_paths'
		})

		cmd.run_first(args, logger)
		for rel in send.call_args[1]['data']['releases']:
			self.assertTrue('type' in rel['module'], rel)

	@mock.patch("opbeatcli.commands.deployment.send_deployment_info")
	def test_run(self, send_deployment_info):
		parser = argparse.ArgumentParser(
			description="Dummy parser")
		subparse = parser.add_subparsers()

		cmd = DeploymentCommand(subparse)

		args = FakeArgs(**{
			'organization_id': 'org_id',
			'app_id': 'app_id',
			'secret_token': 'token',
			'server': 'server',
			'dry_run': 'dry_run',
			'module_name': 'module_name',
			'directory': 'directory',
			'hostname': 'hostname',
			'include_paths': 'include_paths'
		})

		cmd.run_first(args, logger)

		all_args = send_deployment_info.call_args

		positional_args = all_args[0]
		client = positional_args[0]
		self.assertTrue(isinstance(client, Client), client)

		self.assertEqual(positional_args[1], logger)
		self.assertEqual(positional_args[2], args.hostname)
		self.assertEqual(positional_args[3], args.include_paths)
		self.assertEqual(positional_args[4], args.directory)
		self.assertEqual(positional_args[5], args.module_name)

class TestDefaultModuleName(unittest.TestCase):
	def test_with_slash(self):
		directory = '/var/www/opbeat/'
		name = get_default_module_name(directory)

		self.assertEqual(name, "opbeat")

	def test_with_no_slash(self):
		directory = '/var/www/opbeat'
		name = get_default_module_name(directory)

		self.assertEqual(name, "opbeat")

class TestDeployment(unittest.TestCase):
	def setUp(self):
		pass


	@mock.patch('opbeatcli.modprobes.pip_probe.get_ssh_config')
	def test_pass_through_no_config(self, get_ssh_config):
		get_ssh_config.return_value = None
		pass_through_url = "git@github.com:opbeat/opbeatcli.git"

		actual_url = annotate_url_with_ssh_config_info(pass_through_url, logger)

		self.assertEqual(pass_through_url,actual_url)

	@mock.patch('opbeatcli.modprobes.pip_probe.get_ssh_config')
	def test_pass_through(self, get_ssh_config):
		get_ssh_config.return_value = MockSshConfig()
		pass_through_url = "git@github.com:opbeat/opbeatcli.git"

		actual_url = annotate_url_with_ssh_config_info(pass_through_url, logger)

		self.assertEqual(pass_through_url,actual_url)

	@mock.patch('opbeatcli.modprobes.pip_probe.get_ssh_config')
	def test_annotate(self, get_ssh_config):
		get_ssh_config.return_value = MockSshConfig()

		url ='git@opbeat_python:opbeat/opbeat_python.git'
		actual_url = annotate_url_with_ssh_config_info(url, logger)

		self.assertEqual('git@github.com:opbeat/opbeat_python.git',actual_url)

	@mock.patch('opbeatcli.modprobes.pip_probe.get_ssh_config')
	def test_annotate_mercurial(self, get_ssh_config):
		get_ssh_config.return_value = MockSshConfig()

		url = 'ssh://hg@opbeat_python/username/reponame/'
		actual_url = annotate_url_with_ssh_config_info(url, logger)

		self.assertEqual('ssh://hg@github.com/username/reponame/',actual_url)
	
	@mock.patch('opbeatcli.modprobes.pip_probe.get_ssh_config')
	def test_annotate_readonly_url(self, get_ssh_config):
		get_ssh_config.return_value = MockSshConfig()

		url ='git://opbeat_python/roncohen/django-hstore.git'
		actual_url = annotate_url_with_ssh_config_info(url, logger)

		self.assertEqual('git://github.com/roncohen/django-hstore.git',actual_url)
	
	@mock.patch('opbeatcli.modprobes.pip_probe.get_ssh_config')
	def test_pass_through_http(self, get_ssh_config):
		get_ssh_config.return_value = MockSshConfig()

		url ='https://github.com/omab/django-social-auth.git'
		actual_url = annotate_url_with_ssh_config_info(url, logger)

		self.assertEqual(url,actual_url)
