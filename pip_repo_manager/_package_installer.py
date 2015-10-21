class PackageInstaller(object):
    def __init__( self, version_descriptor, path ):
        self.version_descriptor =   version_descriptor
        self.path =                 path


    def __repr__(self):
        return "<PackageInstaller {0} {1}>".format(self.version_descriptor, self.path)
