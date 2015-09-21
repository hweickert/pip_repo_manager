import os
import subprocess
import itertools

from . _git_repo_status import GitRepoStatus



class MultiGit( object ):
    def __init__( self, root_dp, git_executable_fp="git" ):
        self._root_dp = root_dp
        self._git_executable_fp = git_executable_fp


    def gen_statii( self ):
        try:
            git_repo_dps = self.gen_git_repo_dps()
            for git_repo_dp in git_repo_dps:
                git_repo_status = GitRepoStatus( git_repo_dp, self._git_executable_fp )
                git_repo_status.load()
                yield git_repo_status

        except Exception as e:
            print( "{e.__class__.__name__}: {e}".format(e=e) )


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
