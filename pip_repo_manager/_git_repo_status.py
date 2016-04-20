import re
import os
import time
import subprocess
import collections

import colorama
colorama.init()



class GitRepoStatus( list ):
    _rex_log_commit_oneline = re.compile("^[a-z0-9]{7}\s.*$")
    _rex_status_oneline =     re.compile("^[a-zA-Z0-9\s]{2}\s.*$")

    def __init__( self, path, git_executable_fp ):
        list.__init__( self )
        self.path = path
        self._git_executable_fp = git_executable_fp

        self.has_origin = False
        self.has_repository = False
        self.nothing_committed = False
        self.n_commits_behind_origin = 0

        self.load_time = -1


    def contents_modified( self ):
        """ Means the repo does not have any modifications, additions or the like. """

        return self.as_dict() != {}


    def _get_how_many_commits_behind_origin( self ):
        result = 0

        previous_dp = os.curdir
        os.chdir( self.path )

        active_branch = self._get_active_branch()
        if active_branch is None:
            os.chdir( previous_dp )
            raise ValueError( "Unable to query branch for: {0}".format(self.path) )

        list( call_and_gen_output([unicode(self._git_executable_fp), "fetch"]) )

        for line in call_and_gen_output( [unicode(self._git_executable_fp), "log", "HEAD..origin/{0}".format(active_branch), "--oneline"] ):
            if not line.strip():
                continue
            if self._rex_log_commit_oneline.match(line) is None:
                continue
            result += 1

        if result == 0:
            # possibly we are ahead in the number of commits, subtract from result
            for line in call_and_gen_output( [unicode(self._git_executable_fp), "log", "origin/{0}..HEAD".format(active_branch), "--oneline"] ):
                if not line.strip():
                    continue
                if self._rex_log_commit_oneline.match(line) is None:
                    continue
                result -= 1


        os.chdir( previous_dp )

        return result


    def _get_active_branch( self ):
        result = None

        previous_dp = os.curdir
        os.chdir( self.path )

        for line in call_and_gen_output( [unicode(self._git_executable_fp), "rev-parse", "--abbrev-ref", "HEAD"] ):
            result = line.strip()

        os.chdir( previous_dp )

        return result


    def load( self ):
        start_time = time.time()

        if os.path.exists(self.path+"/.git"):
            self.has_repository = True
        else:
            return

        previous_dp = os.curdir

        os.chdir( self.path )

        for line in call_and_gen_output( [self._git_executable_fp, "status", "--porcelain"] ):
            if self._rex_status_oneline.match(line) is None:
                # skip all obsolete lines
                continue
            parts = line.lstrip(" ").split(" ")
            while "" in parts:
                parts.remove( "" )
            if len(parts) != 2:
                raise ValueError( "Invalid log line: {0}".format(line) )

            file_status, file_path = parts[0], parts[1]
            self.append( (file_status, file_path) )

        if "origin" in call_and_gen_output( [self._git_executable_fp, "remote"] ):
            self.has_origin = True
            self.n_commits_behind_origin = self._get_how_many_commits_behind_origin()

        if "fatal: ambiguous argument 'HEAD': unknown revision or path not in the working tree." in call_and_gen_output( [self._git_executable_fp, "rev-list", "HEAD", "--count"], "stderr" ):
            self.nothing_committed = True


        os.chdir( previous_dp )

        end_time = time.time()
        self.load_time = round(end_time - start_time, 2)


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
        repr_string_parts = self._get_repr_string_parts()
        result =            self._get_repr_string_from_parts( repr_string_parts )

        return result


    def _get_repr_string_parts( self ):
        result = [self.__class__.__name__, os.path.basename(self.path)]
        type_counts_string = " ".join(["{0}:{1}".format(t, len(c)) for t, c in self.as_dict().items()])
        if type_counts_string:
            result += [type_counts_string]
        if self.has_repository:
            if not self.has_origin:
                result += [_wrap_in_color("yellow", "MissingOrigin")]
            if self.nothing_committed:
                result += [_wrap_in_color("red", "NothingCommitted")]
        else:
            result += [_wrap_in_color("red", "MissingRepository")]

        if self.n_commits_behind_origin > 0:
            result += [_wrap_in_color("red", "CommitsBehindOrigin:{0}".format(self.n_commits_behind_origin))]
        if self.n_commits_behind_origin < 0:
            result += [_wrap_in_color("red", "CommitsAheadOrigin:{0}".format(abs(self.n_commits_behind_origin)))]

        return result


    def _get_repr_string_from_parts( self, parts ):
        if self.load_time == -1:
            result = "<{0}>".format( " ".join(parts) )
        else:
            result = "<{0} [{1}s]>".format( " ".join(parts), self.load_time )

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
