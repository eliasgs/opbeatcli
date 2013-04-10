import subprocess
import re
from opbeatcli.modprobes import release
from opbeatcli.modprobes.release import (Module, Release)

def run():
	releases = []
	try:
		p = subprocess.Popen(['dpkg', '-l'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		for line in p.stdout:
			pkg = re.split('\s{2,}', line)
			# if package is installed append to result
			if pkg[0] == 'ii': 
				mod = Module(name=pkg[1])
				releases.append(Release(mod, version=pkg[2]))
	finally:
		return releases
