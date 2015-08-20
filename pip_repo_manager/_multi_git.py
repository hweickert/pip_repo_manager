import os
import subprocess
import itertools

from . _git_repo_result import GitRepoStatusResult


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


class MultiGit( object ):
    def __init__( self, root_dp, git_executable_fp="git" ):
        self._root_dp = root_dp
        self._git_executable_fp = git_executable_fp


    def gen_statii( self ):
        previous_dp = os.curdir

        try:
            git_repo_dps = self.gen_git_repo_dps()
            for git_repo_dp in git_repo_dps:
                git_repo_status_result = GitRepoStatusResult( "status", git_repo_dp )
                os.chdir( git_repo_dp )
                for line in call_and_gen_output( [self._git_executable_fp, "status", "--porcelain"] ):
                    file_status, file_path = line.lstrip(" ").split(" ")
                    git_repo_status_result.append( (file_status, file_path) )
                os.chdir( previous_dp )
                yield git_repo_status_result

        except Exception as e:
            print( "{e.__class__.__name__}: {e}".format(e=e) )

        os.chdir( previous_dp )


    def gen_git_repo_dps( self ):
        dps = self._gen_dps( self._root_dp )
        return itertools.ifilter( self._is_git_repo, dps )


    def _gen_dps( self, root_dp ):
        for n in os.listdir( root_dp ):
            if not os.path.isdir( root_dp+"/"+n ):
                continue
            dp = os.path.join(root_dp, n)
            yield dp


    def _is_git_repo( self, dp ):
        return os.path.exists( dp+"/.git" )



if __name__ == "__main__":
    pass
