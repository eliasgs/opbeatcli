from opbeatcli.modprobes import pip_probe
from opbeatcli.modprobes import gem_probe
from opbeatcli.modprobes import dpkg_probe

def all(logger, include_paths, directory, module_name):
	versions = pip_probe.run(logger, include_paths, directory, module_name)
	versions += gem_probe.run()
	versions += dpkg_probe.run()

	return versions
