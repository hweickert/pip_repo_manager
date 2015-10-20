import os

import pip.download
import pip.req.req_file

from . import _setup_py



class RecursiveRequirementGenerator( object ):
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
        self._target_setup_py_fp = target_setup_py_fp
        self._root_source_packages_dp = root_source_packages_dp
        self._destination_sitepackages_dp = destination_sitepackages_dp


    def __iter__( self ):
        self._yielded = []

        require_lines = _setup_py.get_install_requires_lines( self._target_setup_py_fp )
        for requirement in self._gen_requirements_recursive( require_lines ):
            yield requirement


    def _gen_requirements_recursive( self, lines ):
        for requirement in self._gen_requirements_from_lines( lines ):
            if requirement.package_name in self._yielded:
                continue

            source_dir = os.path.join( self._requirements_dp, requirement.package_name )
            if not os.path.exists(source_dir):
                print( "Warning, dependency directory not found and skipped: {0}.".format(source_dir) )
                continue

            requirement.editable = True
            requirement.source_dir = source_dir
            requirement.target_dir = self._destination_sitepackages_dp

            sub_package_names = self._gen_package_names( requirement.setup_py )
            for sub_requirement in self._gen_requirements_recursive( sub_package_names ):
                yield sub_requirement
            yield requirement
            self._yielded.append( requirement.package_name )



    def _gen_requirements_from_lines( self, lines ):
        finder =      None
        comes_from =  None
        options =     None
        session =     pip.download.PipSession()
        wheel_cache = None
        constraint =  False

        for line_number, line in self._gen_line_number_line_tuples( lines ):
            filename = os.path.join( self._root_source_packages_dp, line )
            req_iter = pip.req.req_file.process_line(
                line, filename, line_number, finder,
                comes_from, options, session, wheel_cache,
                constraint=constraint
            )
            for req in req_iter:
                req.package_name = self._get_package_name(line)
                yield req


    def _gen_line_number_line_tuples( self, lines ):
        options = None

        lines = pip.req.req_file.join_lines(lines)
        lines = pip.req.req_file.skip_regex(lines, options)

        for line_number, line in enumerate(lines, 1):
            yield line_number, line


    def _gen_package_names( self, setup_py_fp ):
        lines = _setup_py.get_install_requires_lines( setup_py_fp )
        for line_number, line in self._gen_line_number_line_tuples( lines ):
            yield self._get_package_name( line )


    def _get_package_name( self, line ):
        return line.split("==")[0]
