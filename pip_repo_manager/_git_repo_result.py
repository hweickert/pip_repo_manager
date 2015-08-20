import os
import collections



class GitRepoResult( list ):
    def __init__( self, command, path ):
        list.__init__( self )
        self.command = command
        self.path = path

    def __repr__( self ):
        return "<{0} {1}>".format( self.__class__.__name__, list.__repr__(self) )



class GitRepoStatusResult( GitRepoResult ):
    def is_clean( self ):
        """ Means the repo does not have any modifications, additions or the like. """
        return self.as_dict() == {}


    def as_dict( self ):
        """
            Returns something like:
            >>> {
            >>>     'M':  ['file-a.py', 'file-b.py'],
            >>>     '??': ['file-c.py']
            >>> }
        """
        result = collections.defaultdict(list)
        for type_, value in self:
            result[type_].append( value )
        result = dict(result)
        return result


    def __repr__( self ):
        type_counts_string = " ".join(["{0}:{1}".format(t, len(c)) for t, c in self.as_dict().items()])
        return "<{0} {1} {2}>".format( self.__class__.__name__, os.path.basename(self.path), type_counts_string )
