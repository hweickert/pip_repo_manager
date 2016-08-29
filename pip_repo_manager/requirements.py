import os
import glob

from . import setup_py



def is_linkable_package(package_dp):
    package_code_dp = os.path.join( package_dp, os.path.basename(package_dp) )

    try:
        # if there is a file in the code sub-directory, we can link to it.
        first_n = next(glob.iglob(package_code_dp+"/*"))
    except StopIteration:
        return False
    return True


def get_lines(package_dp):
    result = None

    setup_py_fp =         os.path.join( package_dp, "setup.py" )
    requirements_txt_fp = os.path.join( package_dp, "requirements.txt" )

    if os.path.exists(setup_py_fp):
        print( "Loading '{0}'.".format(setup_py_fp) )
        result = setup_py.get_dict( setup_py_fp )["install_requires"]
    elif os.path.exists(requirements_txt_fp):
        print( "Loading '{0}'.".format(requirements_txt_fp) )
        result = open(requirements_txt_fp, "r").readlines()
    else:
        print( "No requirements for '{0}'.".format(package_dp) )

    return result
