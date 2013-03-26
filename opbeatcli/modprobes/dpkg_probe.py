import subprocess
import re
def run():
	versions = []
	try:
		p = subprocess.Popen(['dpkg', '-l'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		for line in p.stdout:
			pkg = re.split('\s{2,}', line)
			# if package is installed append to result
			if pkg[0] == 'ii': 
				versions.append({
					'version': pkg[2],
					'module':{
						'name': pkg[1]
					}
				})	
	finally:
		return versions
