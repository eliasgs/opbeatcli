from opbeatcli.modprobes import pip_probe
from opbeatcli.modprobes import gem_probe
from opbeatcli.modprobes import dpkg_probe
from opbeatcli.modprobes import npm_probe

def all(logger, include_paths, directory, module_name):
	releases = pip_probe.run(logger, include_paths, directory, module_name)
	releases += gem_probe.run()
	releases += dpkg_probe.run()
	releases += npm_probe.run(directory)

	return releases
