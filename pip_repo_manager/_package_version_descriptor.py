class PackageVersionDescriptor(object):
    def __init__( self, name, comparator, version ):
        self.name =       name
        self.comparator = comparator
        self.version =    version


    def as_string( self ):
        return "{0}{1}{2}".format( self.name, self.comparator, self.version )


    def __repr__(self):
        return "<PackageVersionDescriptor {0} {1} {2}>".format(self.name, self.comparator, self.version)
