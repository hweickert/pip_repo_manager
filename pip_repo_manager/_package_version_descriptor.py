class PackageVersionDescriptor(object):
    def __init__( self, name, comparator, version ):
        self.name =       name
        self.comparator = comparator
        self.version =    version

    def as_string( self ):
        if self.comparator is None or self.version is None:
            result = self.name
        else:
            result = "{0}{1}{2}".format( self.name, self.comparator, self.version )
        return result

    def __repr__(self):
        return "<PackageVersionDescriptor {0} {1} {2}>".format(self.name, self.comparator, self.version)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and hash(self) == hash(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        result = (
            hash(self.name.lower().replace("-", "_"))
        )
        return result
