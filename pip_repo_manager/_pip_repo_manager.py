import sys
import os
import glob
import itertools
import subprocess



class PipRepoManager( object ):
    def __init__( self, root_directory ):
        """
            :param root_directory:

                The root directory that contains all the python packages.
                Call create_index_html() and an index.html file will be created,
                containing all necessary wheel links.
        """

        self._root_directory = os.path.abspath( os.path.expandvars(root_directory) )
        self._index_html_fp = "{0}/index.html".format( root_directory )


    def create_index_html( self, rebuild_wheels=True ):
        """
            Creates a new index.html based on found python packages / wheels.

            Once created you can simply call
                >>> pip install . --find-links <<root_direcory>>
        """

        previous_cur_dir = os.curdir

        try:
            glob_p = "{0}/*/setup.py".format(self._root_directory)

            setup_py_fps = glob.iglob( glob_p )
            package_directories = itertools.imap( os.path.dirname, setup_py_fps )
            if rebuild_wheels:
                package_directories = self.gen_create_wheels( package_directories )
            wheel_fps = self.gen_wheel_filepaths( package_directories )
            link_lines = itertools.imap( self.get_link_line, wheel_fps )

            written_lines = self._write_index_html( link_lines )
            written_lines = list(written_lines)

            print "\n\nCreated {0}:".format( self._index_html_fp )
            print "\n".join(written_lines)

        except Exception as e:
            print( "{e.__class__.__name__}: {e}".format(e=e) )

        os.chdir( previous_cur_dir )


    @classmethod
    def gen_create_wheels( cls, package_directories ):
        return itertools.imap( cls.create_wheel, package_directories )


    @classmethod
    def create_wheel( cls, package_dp ):
        os.chdir( package_dp )
        subprocess.call( ["python", "setup.py", "bdist_wheel"] )
        return package_dp


    @classmethod
    def gen_wheel_filepaths( cls, package_directories ):
        for package_dp in package_directories:
            wheel_glob_fp = "{0}/dist/*.whl".format( package_dp )
            for wheel_fp in glob.iglob( wheel_glob_fp ):
                yield wheel_fp


    @classmethod
    def get_link_line( cls, wheel_fp ):
        file_url = "file://" + wheel_fp.replace("\\", "/")
        return r"""<a href="{0}">{1}</a>""".format( file_url, os.path.basename(file_url) )


    def _write_index_html( self, link_lines ):
        with open( self._index_html_fp, "w" ) as f:
            for link_line in link_lines:
                f.write( link_line + "\n<br>\n" )
                yield link_line

