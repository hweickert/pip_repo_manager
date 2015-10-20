import imp
import setuptools



def get_install_requires_lines( setup_py_fp ):
    result = []
    _hijack_setuptools( result, setup_py_fp )
    return result


def _hijack_setuptools(result_buffer, setup_py_fp):
    setup_tools_setup_original = setuptools.setup
    setuptools.setup = lambda *a, **kwa: result_buffer.extend( kwa.get("install_requires", []) )
    imp.load_source( "setup", setup_py_fp )
    setuptools.setup = setup_tools_setup_original
