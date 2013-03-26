import subprocess
import re
def run():
	versions = []
	try:
		p = subprocess.Popen(['gem', 'list'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		for line in p.stdout:
			if line != '' and not re.match('^[*].*', line):
				pkg = re.split('\s|[()]', line)
				versions.append({
					'version': pkg[2],
					'module':{
						'name': pkg[0]
					}
				})	
	finally:
		return []
