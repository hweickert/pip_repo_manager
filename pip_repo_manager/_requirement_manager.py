import os
import subprocess
import platform

from . import _setup_py
from . _package_version_descriptor import PackageVersionDescriptor
from . _package_installer          import PackageInstaller



def install_project_dependencies( project_dp, as_link=True ):
    """
        Highest level installation functions.
        Requires a project directory path.
    """

    setup_py_fp =                 _get_setup_py_fp( project_dp )
    root_source_packages_dp =     os.path.dirname( project_dp )
    destination_sitepackages_dp = _get_destination_sitepackages_dp( project_dp )

    requirement_manager = RequirementManager( setup_py_fp, root_source_packages_dp, destination_sitepackages_dp )
    for package_installer in requirement_manager.gen_package_installers():
        requirement_manager.install_package( package_installer, as_link=as_link )


def _get_setup_py_fp(project_dp):
    result = project_dp+"/setup.py"
    if not os.path.exists( result ):
        raise ValueError( "Required 'setup.py' not found: {0}".format(result) )
    return result


def install(setup_py_fp, root_source_packages_dp, destination_sitepackages_dp, as_link=True):
    requirement_manager = RequirementManager(setup_py_fp, root_source_packages_dp, destination_sitepackages_dp)
    for package_installer in requirement_manager.gen_package_installers():
        requirement_manager.install_package( package_installer, as_link )



def _get_destination_sitepackages_dp( project_dp ):
    venv_destination_sitepackages_dp = project_dp + "/venv/Lib/site-packages"
    env_destination_sitepackages_dp =  project_dp + "/env/Lib/site-packages"

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
        :target_setup_py_fp:.

        :root_source_packages_dp:
            Points to a directory where the requested requirements are stored.
            Each repository's own setup.py file will be checked for requirements (recursively).

        :destination_sitepackages_dp:
            Is the directory where the resulting requirements (in form of 'pth' files) would
            be generated (if the requirement.install() function gets called. ).
    """

    def __init__( self, target_setup_py_fp, root_source_packages_dp, destination_sitepackages_dp ):
        self._target_setup_py_fp =          target_setup_py_fp
        self._root_source_packages_dp =     root_source_packages_dp
        self._destination_sitepackages_dp = destination_sitepackages_dp


    def install_package( self, package_installer, as_link=True ):
        self._as_link = as_link
        self._package_installer = package_installer
        self._pip_executable_fp = self._get_existing_pip_executable_fp()
        self._install_package()


    def _get_existing_pip_executable_fp( self ):
        result = self._get_pip_executable_fp()
        if not os.path.exists( result ):
            raise Exception( "Target pip executable not found: {0}".format(self._pip_executable_fp) )
        return result


    def _install_package( self ):
        print "Installing: {0}".format(self._package_installer.version_descriptor.name)
        if self._package_is_locally_available():
            if self._as_link:
                self._install_local_package_via_pth_link()
            else:
                self._install_local_package_regularly()
        else:
            self._install_foreign_package_regularly()


    def _package_is_locally_available( self ):
        return self._package_installer.path is not None

    def _install_local_package_via_pth_link( self ):
        pth_fp = self._destination_sitepackages_dp + "/{0}.pth".format( self._package_installer.version_descriptor.name )
        with open( pth_fp, "w" ) as f:
            f.write( self._package_installer.path )
        print "Written: {0}".format(pth_fp)


    def _install_local_package_regularly( self ):
        subprocess.call( [self._pip_executable_fp, "install", self._package_installer.version_descriptor.as_string(), "--find-links", self._root_source_packages_dp] )


    def _install_foreign_package_regularly( self ):
        subprocess.call( [self._pip_executable_fp, "install", self._package_installer.version_descriptor.as_string()] )


    def gen_package_installers( self ):
        self._yielded = []
        for package_installer in self._gen_package_installers_recursive( self._target_setup_py_fp ):
            yield package_installer


    def _get_pip_executable_fp( self ):
        if platform.system() == "Windows":
            result = os.path.abspath( self._destination_sitepackages_dp+"/../../Scripts/pip.exe" )
        else:
            raise NotImplementedError( "Cannot guess pip executable path for this platform." )

        return result


    def _gen_package_installers_recursive( self, setup_py_fp ):
        require_lines = _setup_py.get_install_requires_lines( setup_py_fp )

        for package_version_descriptor in self._gen_package_version_descriptors( require_lines ):
            if package_version_descriptor.name in self._yielded:
                continue

            self._yielded.append( package_version_descriptor.name )

            package_dp =          os.path.join(   self._root_source_packages_dp, package_version_descriptor.name )
            package_setup_py_fp = os.path.join(   package_dp, "setup.py" )

            if os.path.exists( package_setup_py_fp ):
                exists = True
                for package_installer in self._gen_package_installers_recursive( package_setup_py_fp ):
                    yield package_installer
            else:
                exists = False

            if exists is False:
                package_dp = None

            yield PackageInstaller( package_version_descriptor, package_dp )


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



if __name__ == "__main__":
    install_project_dependencies( r"D:\hweickert\dev\vfx\local\mv_vfx_naming", as_link=False )
