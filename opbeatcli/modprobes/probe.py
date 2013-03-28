from opbeatcli.modprobes import pip_probe
from opbeatcli.modprobes import gem_probe
from opbeatcli.modprobes import dpkg_probe

def all(logger, include_paths, directory, module_name):
	releases = pip_probe.run(logger, include_paths, directory, module_name)
	releases += gem_probe.run()
	releases += dpkg_probe.run()

	return releases
