import os
import subprocess
import platform

from . import _setup_py
from . _package_version_descriptor import PackageVersionDescriptor
from . _package_installer          import PackageInstaller



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


    def gen_package_installers( self ):
        self._yielded = []
        return self._gen_package_installers_recursive( self._target_setup_py_fp )


    def install( self, package_installer ):
        print "Installing: {0}".format(package_installer.version_descriptor.name)

        pip_executable_fp = self._get_pip_executable_fp()
        if not os.path.exists( pip_executable_fp ):
            raise Exception( "Target pip executable not found: {0}".format(pip_executable_fp) )

        if package_installer.path is None:
            subprocess.call( [pip_executable_fp, "install", package_installer.version_descriptor.as_string()] )
        else:
            pth_fp = self._destination_sitepackages_dp + "/{0}.pth".format( package_installer.version_descriptor.name )
            with open( pth_fp, "w" ) as f:
                f.write( package_installer.path )
            print "Written: {0}".format(pth_fp)


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
    setup_py_fp =                 r"D:\hweickert\dev\mv_vfx_mirror_timelogs\setup.py"
    root_source_packages_dp =     r"D:\hweickert\dev\vfx\local"
    destination_sitepackages_dp = r"D:\hweickert\dev\mv_vfx_mirror_timelogs\venv\Lib\site-packages"

    requirement_manager = RequirementManager(setup_py_fp, root_source_packages_dp, destination_sitepackages_dp)
    for package_installer in requirement_manager.gen_package_installers():
        requirement_manager.install( package_installer )
