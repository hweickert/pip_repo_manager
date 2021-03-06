import sys
import os
import glob
import itertools
import subprocess

from . _multi_git import MultiGit
from . import _requirement_manager
from . _git_repo_status import GitRepoStatus



class PipRepoManager(object):
    def __init__(self, root_directory, git_executable_fp="git"):
        """
            :param root_directory:

                The root directory that contains all the python packages.
                Call create_index_html() and an index.html file will be created,
                containing all necessary wheel links.
        """

        self._root_directory = os.path.abspath(os.path.expandvars(root_directory))
        self._git_executable_fp = git_executable_fp


    def gen_dependencies(self, project_dp, root_source_packages_dp, recursive=True):
        for dependency in _requirement_manager.gen_dependencies(project_dp, root_source_packages_dp, recursive):
            yield dependency


    def install_dependencies(self, project_dp, root_source_packages_dp, environment=None, target_dp=None):
        _requirement_manager.install_project_dependencies(
            project_dp,
            root_source_packages_dp=root_source_packages_dp,
            as_link=False,
            environment=environment,
            destination_sitepackages_dp=target_dp
        )


    def install_dependencies_develop(self, project_dp, root_source_packages_dp, environment=None, target_dp=None):
        _requirement_manager.install_project_dependencies(
            project_dp,
            root_source_packages_dp=root_source_packages_dp,
            as_link=True,
            environment=environment,
            destination_sitepackages_dp=target_dp
       )


    def multi_git_gui(self):
        mg = MultiGit(self._root_directory, self._git_executable_fp)

        git_repo_statii = mg.gen_statii()
        git_repo_statii = itertools.ifilter(self._should_be_git_gui_listed, git_repo_statii)

        print("\n\n")
        for git_repo_status in git_repo_statii:
            print git_repo_status
            subprocess.call([self._git_executable_fp, "gui"])


    def git_status(self):
        git_repo_status = GitRepoStatus(self._root_directory, self._git_executable_fp)
        git_repo_status.load()
        self.print_repo_status_queried(git_repo_status)
        print git_repo_status


    def multi_git_status(self):
        mg = MultiGit(self._root_directory, self._git_executable_fp)

        print "Querying repository statii ..."
        git_repo_statii = mg.gen_statii(include_non_repositories=True)
        git_repo_statii = itertools.imap(   self.print_repo_status_queried, git_repo_statii)
        git_repo_statii = itertools.ifilter(self._should_be_git_status_listed, git_repo_statii)
        git_repo_statii = reversed(sorted(git_repo_statii, cmp=self._git_status_sort_func))

        for git_repo_status in git_repo_statii:
            print git_repo_status


    def print_repo_status_queried(self, grs):
        name = os.path.basename(grs.path)
        print("- {0}".format(name))
        return grs


    def _git_status_sort_func(self, grs_a, grs_b):
        result = 0
        result = cmp(result, cmp(not grs_a.has_repository, not grs_b.has_repository))
        result = cmp(result, cmp(not grs_a.has_origin, not grs_b.has_origin))
        result = cmp(result, cmp(grs_a.path, grs_b.path))
        return result


    def multi_git_pull_origin(self):
        mg = MultiGit(self._root_directory, self._git_executable_fp)

        git_repo_statii = mg.gen_statii()
        git_repo_statii = itertools.ifilter(lambda grs: grs.has_origin, git_repo_statii)

        for git_repo_status in git_repo_statii:
            print git_repo_status

            proc = subprocess.Popen([self._git_executable_fp, "rev-parse", "--abbrev-ref", "HEAD"], stdout=subprocess.PIPE)
            for line in iter(proc.stdout.readline,''):
                branch = line.rstrip()
                break

            previous_cur_dir = os.curdir
            os.chdir(git_repo_status.path)
            subprocess.call([self._git_executable_fp, "pull", "origin", branch])

            if os.path.exists(self._root_directory+"/.gitmodules"):
                subprocess.call([self._git_executable_fp, "submodule", "update"])

            os.chdir(previous_cur_dir)



    def _should_be_git_gui_listed(self, grs):
        return grs.contents_modified() or not grs.has_origin


    def _should_be_git_status_listed(self, grs):
        result = \
            grs.contents_modified() or \
            not grs.has_repository or \
            not grs.has_origin or \
            grs.nothing_committed or \
            grs.branch_non_master or \
            grs.n_commits_behind_origin != 0

        return result


    def create_wheel(self, project_name):
        """
            (Re-)builds the wheel for the given project via
                >>> project_name/python setup.py bdist_wheel
        """

        previous_cur_dir = os.curdir

        try:
            package_dp = os.path.join(self._root_directory, project_name)
            self.create_wheel_for_package(package_dp)

        except Exception as e:
            print("{e.__class__.__name__}: {e}".format(e=e))

        os.chdir(previous_cur_dir)


    def create_index_html(self, rebuild_wheels=True, root_source_packages_dp=None):
        """
            Creates a new index.html based on found python packages / wheels.

            Once created you can simply call
                >>> pip install . --find-links <<root_direcory>>
        """

        previous_cur_dir = os.curdir
        root_source_packages_dp = self._root_directory if root_source_packages_dp is None else root_source_packages_dp

        try:
            glob_p = "{0}/*/setup.py".format(root_source_packages_dp)

            setup_py_fps = glob.iglob(glob_p)
            package_directories = itertools.imap(os.path.dirname, setup_py_fps)
            if rebuild_wheels:
                package_directories = self.gen_create_wheels(package_directories)
            wheel_fps = self.gen_wheel_filepaths(package_directories)
            link_lines = itertools.imap(self.get_link_line, wheel_fps)

            index_html_fp = "{0}/index.html".format(root_source_packages_dp)
            written_lines = self._write_index_html(index_html_fp, link_lines)
            written_lines = list(written_lines)

            print "\n\nCreated {0}:".format(index_html_fp)
            print "\n".join(written_lines)

        except Exception as e:
            print("{e.__class__.__name__}: {e}".format(e=e))

        os.chdir(previous_cur_dir)


    @classmethod
    def gen_create_wheels(cls, package_directories):
        return itertools.imap(cls.create_wheel_for_package, package_directories)


    @classmethod
    def create_wheel_for_package(cls, package_dp):
        os.chdir(package_dp)
        subprocess.call(["python", "setup.py", "bdist_wheel"])
        return package_dp


    @classmethod
    def gen_wheel_filepaths(cls, package_directories):
        for package_dp in package_directories:
            wheel_glob_fp = "{0}/dist/*.whl".format(package_dp)
            for wheel_fp in glob.iglob(wheel_glob_fp):
                yield wheel_fp


    @classmethod
    def get_link_line(cls, wheel_fp):
        file_url = "file://" + wheel_fp.replace("\\", "/")
        return r"""<a href="{0}">{1}</a>""".format(file_url, os.path.basename(file_url))


    def _write_index_html(self, index_html_fp, link_lines):
        with open(index_html_fp, "w") as f:
            for link_line in link_lines:
                f.write(link_line + "\n<br>\n")
                yield link_line

