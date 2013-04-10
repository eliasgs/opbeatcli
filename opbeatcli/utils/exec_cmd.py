import subprocess
import re
def exec_cmd(command):
    """Return the STDOUT as a open file object"""
    args = re.split('\s+', command)
    try:
        p = subprocess.Popen(args, stdout=subprocess.PIPE)
    except OSError:
        return iter([])
    else:
        return p.stdout
