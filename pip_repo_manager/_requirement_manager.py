import os
import subprocess
import platform

from . import requirements
from . _package_version_descriptor import PackageVersionDescriptor
from . _package_installer          import PackageInstaller



def install_project_dependencies( project_dp, root_source_packages_dp=None, as_link=True, environment=None, destination_sitepackages_dp=None ):
    """
        Highest level installation functions.
        Requires a project directory path.
    """

    root_source_packages_dp =     root_source_packages_dp

    if destination_sitepackages_dp is None:
        destination_sitepackages_dp = _get_destination_sitepackages_dp( project_dp, environment )

    install( project_dp, root_source_packages_dp, destination_sitepackages_dp, as_link=as_link )


def gen_dependencies( project_dp, root_source_packages_dp, recursive=True ):
    for package_installer in _gen_package_installers( project_dp, root_source_packages_dp, destination_sitepackages_dp="dummy", recursive=recursive ):
        yield (package_installer.version_descriptor, package_installer.path)


def install( project_dp, root_source_packages_dp, destination_sitepackages_dp, as_link=True ):
    requirement_manager = RequirementManager( project_dp, root_source_packages_dp, destination_sitepackages_dp )
    for package_installer in _gen_package_installers( project_dp, root_source_packages_dp, destination_sitepackages_dp, recursive=True ):
        requirement_manager.install_package( package_installer, as_link )


def create_pth_link( destination_sitepackages_dp, name, target_repository_dp ):
    pth_fp = "{destination_sitepackages_dp}/{name}.pth".format( **locals() )
    with open( pth_fp, "w" ) as f:
        f.write( target_repository_dp )
    print "Written: {pth_fp}".format(**locals())


def _gen_package_installers( project_dp, root_source_packages_dp, destination_sitepackages_dp, recursive=True ):
    project_dn = os.path.basename( project_dp )

    requirement_manager = RequirementManager(project_dp, root_source_packages_dp, destination_sitepackages_dp)
    for package_installer in requirement_manager.gen_package_installers( recursive=recursive ):
        yield package_installer


def _get_destination_sitepackages_dp( project_dp, environment ):
    venv_destination_sitepackages_dp = project_dp + "/venv/Lib/site-packages"
    env_destination_sitepackages_dp =  project_dp + "/env/Lib/site-packages"

    if environment is not None:
        result = "{0}/{1}/Lib/site-packages".format(project_dp, environment)
        if not os.path.exists(result):
            raise ValueError( "Unable to find environment directory: \n  {0}".format(result) )
        return result

    if os.path.exists(venv_destination_sitepackages_dp):
        result = venv_destination_sitepackages_dp
    elif os.path.exists(env_destination_sitepackages_dp):
        result = env_destination_sitepackages_dp
    else:
        raise ValueError( "Unable to find existing venv/env directory: \n  {0}\n  {1}".format(venv_destination_sitepackages_dp, env_destination_sitepackages_dp) )

    return result



class RequirementManager( object ):
    r"""
        Generates editable requirement instances based on the given
        :target_package_dp:.

        :root_source_packages_dp:
            Points to a directory where the requested requirements are stored.
            Each repository's own setup.py file will be checked for requirements (recursively).

        :destination_sitepackages_dp:
            Is the directory where the resulting requirements (in form of 'pth' files) would
            be generated (if the requirement.install() function gets called. ).
    """

    def __init__( self, target_package_dp, root_source_packages_dp, destination_sitepackages_dp ):
        self._target_package_dp =           target_package_dp
        self._root_source_packages_dp =     root_source_packages_dp
        self._destination_sitepackages_dp = destination_sitepackages_dp


    def install_package( self, package_installer, as_link=True ):
        self._as_link =           as_link
        self._package_installer = package_installer

        self._pip_executable_fp = self._get_existing_pip_executable_fp()

        self._install_package()


    def _create_pth_link( self, name, target_repository_dp ):
        create_pth_link( self._destination_sitepackages_dp, name, target_repository_dp )


    def _get_existing_pip_executable_fp( self ):
        result = self._get_pip_executable_fp()
        if not os.path.exists( result ):
            # ok, pip wasn't found but maybe it is on the PATH variable
            result = "pip"
        return result


    def _install_package( self ):
        print "Installing: {0}".format(self._package_installer.version_descriptor.name)
        if self._package_is_locally_available():
            if self._as_link:
                self._create_pth_link( self._package_installer.version_descriptor.name, self._package_installer.path )
            else:
                self._install_local_package()
        else:
            self._install_foreign_package()


    def _package_is_locally_available( self ):
        return self._package_installer.path is not None


    def _install_local_package( self ):
        # ignore dependencies because we deal with them by ourself
        command = [self._pip_executable_fp, "install", self._package_installer.version_descriptor.as_string(), "--no-dependencies", "--find-links", self._root_source_packages_dp, "--target", self._destination_sitepackages_dp]
        subprocess.call( command )


    def _install_foreign_package( self ):
        subprocess.call( [self._pip_executable_fp, "install", self._package_installer.version_descriptor.as_string(), "--target", self._destination_sitepackages_dp] )


    def gen_package_installers( self, recursive=True ):
        self._yielded = []
        project_name = os.path.basename(self._target_package_dp)
        for package_installer in self._gen_package_installers_recursive( self._target_package_dp, recursive ):
            # in case there is a cyclic dependency, refering to the original project name, skip it
            if package_installer.version_descriptor.name == project_name:
                continue
            yield package_installer


    def _get_pip_executable_fp( self ):
        if platform.system() == "Windows":
            result = os.path.abspath( self._destination_sitepackages_dp+"/../../Scripts/pip.exe" )
        else:
            raise NotImplementedError( "Cannot guess pip executable path for this platform." )

        return result


    def _gen_package_installers_recursive( self, package_dp, recursive ):
        require_lines = requirements.get_lines( package_dp )
        if not require_lines:
            return

        for package_version_descriptor in self._gen_package_version_descriptors( require_lines ):
            if package_version_descriptor.name in self._yielded:
                continue

            self._yielded.append( package_version_descriptor.name )

            sub_package_dp = os.path.join(   self._root_source_packages_dp, package_version_descriptor.name )

            if requirements.is_linkable_package( sub_package_dp ):
                exists = True
                if recursive:
                    for package_installer in self._gen_package_installers_recursive( sub_package_dp, recursive=recursive ):
                        yield package_installer
            else:
                exists = False

            if exists is False:
                sub_package_dp = None

            yield PackageInstaller( package_version_descriptor, sub_package_dp )


    def _gen_package_version_descriptors( self, lines ):
        for line in lines:
            package_name = line
            package_comparator = None
            package_version = None
            for comparator in ("==", ">", ">=", "<", "<=", "!="):
                if line.find(comparator) != -1:
                    package_name, package_version = line.split(comparator)
                    package_comparator = comparator
                    break
            yield PackageVersionDescriptor( package_name, package_comparator, package_version )
