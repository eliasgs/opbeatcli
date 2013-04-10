import subprocess
import re
def exec_cmd(command):
    """Return the STDOUT as a open file object"""
    args = re.split('\s+', command)
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    
    return p.stdout
