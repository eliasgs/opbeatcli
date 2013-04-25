import subprocess
import re
from opbeatcli.utils.exec_cmd import exec_cmd
from opbeatcli.modprobes.release import (Module, Release)

def run():
    releases = []
    output = exec_cmd('dpkg -l')

    for line in output:
        pkg = re.split('\s{2,}', line)
        # if package is installed append to result
        if pkg[0] == 'ii': 
            mod = Module(name=pkg[1], module_type='deb')
            releases.append(Release(mod, version=pkg[2]))
    return releases
