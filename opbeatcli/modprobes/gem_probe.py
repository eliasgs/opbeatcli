import subprocess
import re
from opbeatcli.modprobes import release

def run():
	releases = []
	try:
		p = subprocess.Popen(['gem', 'list'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		for line in p.stdout:
			if line != '' and not re.match('^[*]', line):
				pkg = re.split('\s|[()]', line)
				mod = Module(name=pkg[0])
				releases.append(Release(mod, version=pkg[2]))
	finally:
		return releases
