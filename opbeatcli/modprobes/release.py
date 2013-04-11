class Module(object):
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Vcs(object):
    def __init__(self, vcs_type, revision, repository, branch):
        self.vcs_type = vcs_type
        self.revision = revision
        self.repository = repository
        self.branch = branch

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Release(object):
    def __init__(self, module, version=None, vcs=None):
        self.module = module
        self.version = version
        self.vcs = vcs

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
