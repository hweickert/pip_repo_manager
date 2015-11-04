import os
import collections
import subprocess

import colorama
colorama.init()



class GitRepoStatus( list ):
    def __init__( self, path, git_executable_fp ):
        list.__init__( self )
        self.path = path
        self._git_executable_fp = git_executable_fp

        self.has_origin = False
        self.has_repository = False
        self.nothing_committed = False


    def contents_modified( self ):
        """ Means the repo does not have any modifications, additions or the like. """

        return self.as_dict() != {}


    def load( self ):
        if os.path.exists(self.path+"/.git"):
            self.has_repository = True
        else:
            return

        previous_dp = os.curdir

        os.chdir( self.path )

        for line in call_and_gen_output( [self._git_executable_fp, "status", "--porcelain"] ):
            try:
                file_status, file_path = line.lstrip(" ").split(" ")
            except ValueError:
                break
            self.append( (file_status, file_path) )

        if "origin" in call_and_gen_output( [self._git_executable_fp, "remote"] ):
            self.has_origin = True

        if "fatal: ambiguous argument 'HEAD': unknown revision or path not in the working tree." in call_and_gen_output( [self._git_executable_fp, "rev-list", "HEAD", "--count"], "stderr" ):
            self.nothing_committed = True

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
        parts = [self.__class__.__name__, os.path.basename(self.path)]

        type_counts_string = " ".join(["{0}:{1}".format(t, len(c)) for t, c in self.as_dict().items()])
        if type_counts_string:
            parts += [type_counts_string]
        if self.has_repository:
            if not self.has_origin:
                parts += [_wrap_in_color("yellow", "MissingOrigin")]
            if self.nothing_committed:
                parts += [_wrap_in_color("red", "NothingCommitted")]
        else:
            parts += [_wrap_in_color("red", "MissingRepository")]

        result = "<{0}>".format( " ".join(parts) )

        # if not self.has_repository:
        #     result = "{0}{1}{2}".format(colorama.Fore.CYAN, result, colorama.Style.RESET_ALL)
        # else:
        #     result = "{0}{1}{2}".format(colorama.Style.BRIGHT, result, colorama.Style.RESET_ALL)

        return result



def _wrap_in_color( color, s ):
    color_string = getattr(colorama.Fore, color.upper())
    return colorama.Style.BRIGHT+"{0}{1}{2}".format(color_string, s, colorama.Style.RESET_ALL)


def call_and_gen_output( command_line, mode="stdout" ):
    """
        Inspired by:
            http://blog.endpoint.com/2015/01/getting-realtime-output-using-python.html
    """

    process = subprocess.Popen( command_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
    stream = getattr(process, mode)
    while True:
        line = stream.readline()
        if line == '' and process.poll() is not None:
            break
        if line:
            yield line.rstrip()
    # exit_code = process.poll()
    # yield exit_code


