import subprocess
import re
from opbeatcli.utils.exec_cmd import exec_cmd
from opbeatcli.modprobes.release import (Module, Release)


def to_releases(output):
    print output
    releases = []
    for line in output:
        if re.match('.*@', line):
            pkg = re.split('\s+', line)
            pkg = re.split('@', pkg[1])
            mod = Module(name=pkg[0])
            releases.append(Release(mod, version=pkg[1]))

    return releases

def run(directory=None):
    # Global packages

    releases = []
    releases = to_releases(exec_cmd('npm ls -g --depth=0'))
    
    # Local packages
    releases += to_releases(exec_cmd('npm ls --depth=0', directory))

    return releases
