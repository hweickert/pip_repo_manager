import os
import collections
import subprocess



class GitRepoStatus( list ):
    def __init__( self, path, git_executable_fp ):
        list.__init__( self )
        self.path = path
        self._git_executable_fp = git_executable_fp


    def is_clean( self ):
        """ Means the repo does not have any modifications, additions or the like. """
        return self.as_dict() == {}


    def load( self ):
        previous_dp = os.curdir
        os.chdir( self.path )
        for line in call_and_gen_output( [self._git_executable_fp, "status", "--porcelain"] ):
            try:
                file_status, file_path = line.lstrip(" ").split(" ")
            except ValueError:
                break
            self.append( (file_status, file_path) )
        os.chdir( previous_dp )


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



def call_and_gen_output( command_line ):
    """
        Inspired by:
            http://blog.endpoint.com/2015/01/getting-realtime-output-using-python.html
    """

    process = subprocess.Popen(command_line, stdout=subprocess.PIPE)
    while True:
        line = process.stdout.readline()
        if line == '' and process.poll() is not None:
            break
        if line:
            yield line.rstrip()
    # exit_code = process.poll()
    # yield exit_code


