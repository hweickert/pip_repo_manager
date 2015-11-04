import os
import subprocess
import itertools

from . _git_repo_status import GitRepoStatus



class MultiGit( object ):
    def __init__( self, root_dp, git_executable_fp="git", include_root_git_dp=True ):
        self._root_dp = root_dp
        self._git_executable_fp = git_executable_fp
        self._include_root_git_dp = include_root_git_dp


    def gen_statii( self, include_non_repositories=False ):
        try:
            git_repo_dps = self.gen_git_repo_dps( include_non_repositories )
            for git_repo_dp in git_repo_dps:
                git_repo_status = GitRepoStatus( git_repo_dp, self._git_executable_fp )
                git_repo_status.load()
                yield git_repo_status

        except Exception as e:
            print( "{e.__class__.__name__}: {e}".format(e=e) )


    def gen_git_repo_dps( self, include_non_repositories=False ):
        dps = self._gen_dps( self._root_dp )
        dps = itertools.ifilterfalse( lambda dp: os.path.basename(dp) == ".git", dps )
        if not include_non_repositories:
            dps = itertools.ifilter(      self._dot_git_subdirectory_or_file_exists, dps )
        result = dps
        return result


    def _gen_dps( self, root_dp ):
        if self._include_root_git_dp:
            yield os.path.join( self._root_dp )

        for n in os.listdir( root_dp ):
            if not os.path.isdir( root_dp+"/"+n ):
                continue
            dp = os.path.join(root_dp, n)
            yield dp


    def _dot_git_subdirectory_or_file_exists( self, dp ):
        return os.path.exists( dp+"/.git" )



if __name__ == "__main__":
    pass
