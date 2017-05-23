import os
import sys
import setuptools
import mock



def get_dict(setup_py_fp):
    result = {}
    _hijack_setuptools( result, setup_py_fp )
    return result


def _hijack_setuptools(result_buffer_dict, setup_py_fp):
    setup_py_dp = os.path.dirname(setup_py_fp)
    sys.path.insert(0, setup_py_dp)
    def stub_setup_func(*a, **kwa):
        result_buffer_dict["install_requires"] = kwa.get("install_requires", [])
        result_buffer_dict["version"] = kwa.get("version", None)
    setuptools_stub = mock.MagicMock()
    setuptools_stub.setup = stub_setup_func

    with mock.patch.dict('sys.modules', setuptools=setuptools_stub):
        import setup
    sys.path.pop(0)




if __name__ == "__main__":
    print get_dict(r"C:\mv\tools_vfx\vfx\production/mv_vfx_maya\setup.py")
