import subprocess
import os
import re
def exec_cmd(command, diretory=None):
    """Return the STDOUT as a open file object."""
    args = re.split('\s+', command)
    try:
        p = subprocess.Popen(args,
                             stdout=subprocess.PIPE,
                             stderr=open(os.devnull, 'w'),
                             cwd=diretory)
    except OSError:
        return iter([])
    else:
        return p.stdout
