import re
from opbeatcli.utils.exec_cmd import exec_cmd
from opbeatcli.modprobes.release import (Module, Release)

def run():
    releases = []
    output = exec_cmd('gem list')

    for line in output:
        if line != '' and not re.match('^[*]', line):
            pkg = re.split('\s|[()]', line)
            mod = Module(name=pkg[0], module_type='gem')
            releases.append(Release(mod, version=pkg[2]))
    return releases
