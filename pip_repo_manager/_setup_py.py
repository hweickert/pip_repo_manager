import imp
import setuptools



def get_dict( setup_py_fp ):
    result = {}
    _hijack_setuptools( result, setup_py_fp )
    return result


def _hijack_setuptools(result_buffer_dict, setup_py_fp):
    setup_tools_setup_original = setuptools.setup
    def stub_setup_func( *a, **kwa ):
        result_buffer_dict["install_requires"] = kwa.get("install_requires",   [])
        result_buffer_dict["version"] =          kwa.get("version",          None)

    setuptools.setup = stub_setup_func
    imp.load_source( "setup", setup_py_fp )
    setuptools.setup = setup_tools_setup_original
