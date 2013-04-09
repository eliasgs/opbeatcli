class Module(object):
    def __init__(self, name):
        self.name = name

class Vcs(object):
    def __init__(self, vcs_type, revision, repository, branch):
        self.vcs_type = vcs_type
        self.revision = revision
        self.repository = repository
        self.branch = branch

class Relase(object):
    def __init__(self, module, version, vcs):
        self.module = module
        self.version = version
        self.vcs = vcs
