import os
import argparse

from . _pip_repo_manager import PipRepoManager
from . import _requirement_manager



def main():
    args = _get_args()

    pip_repo_manager = PipRepoManager( args.root_directory, args.git_fp )

    if args.command == "create_wheel":
        if args.project is None:
            raise ValueError( "'--project' must be set when using the 'create_wheel' command." )
        pip_repo_manager.create_wheel( args.project )

    elif args.command == "install_dependencies":
        if args.project_path is None:
            raise ValueError( "'--project_path' must be set when using the 'install_dependencies' command." )
        pip_repo_manager.install_dependencies(args.project_path, args.root_directory, environment=args.environment, target_dp=args.target_path)
        if args.include_project:
            name = os.path.basename(args.project_path)
            _requirement_manager.create_pth_link( args.target_path, name, args.project_path )

    elif args.command == "install_dependencies_develop":
        if args.project_path is None:
            raise ValueError( "'--project_path' must be set when using the 'install_dependencies_develop' command." )
        pip_repo_manager.install_dependencies_develop(args.project_path, args.root_directory, environment=args.environment, target_dp=args.target_path)
        if args.include_project:
            name = os.path.basename(args.project_path)
            _requirement_manager.create_pth_link( args.target_path, name, args.project_path )

    elif args.command == "index":
        pip_repo_manager.create_index_html()

    elif args.command == "git_status":
        pip_repo_manager.git_status()

    elif args.command == "git_multi_status":
        pip_repo_manager.multi_git_status()

    elif args.command == "git_gui":
        pip_repo_manager.multi_git_gui()

    elif args.command == "git_pull_origin":
        pip_repo_manager.multi_git_pull_origin()

    else:
        raise ValueError( "Unknown command: '{0}'".format(parser.command) )



def _get_args():
    parser = argparse.ArgumentParser(description='PipRepoManager.')

    parser.add_argument(
        "command", choices=[
            "index",
            "create_wheel",
            "install_dependencies_develop",
            "install_dependencies",
            "git_status",
            "git_multi_status",
            "git_gui",
            "git_pull_origin"
        ], default="index", type=unicode,
        help="What command to execute."
    )

    parser.add_argument(
        "root_directory", type=_absolute_path,
        help="The directory that contains all the python package repositories." )

    parser.add_argument(
        "--project", default=None,
        help="The project to work on. Used in conjunction with 'create_wheel'." )

    parser.add_argument(
        "--project_path", default=None, type=_absolute_path,
        help="The project path to work on. Used in conjunction with 'install_dependencies'." )

    parser.add_argument(
        "--target_path", default=None, type=_absolute_path,
        help="The target installation directory (e.g. 'site-packages') to install the python package and its' dependencies into. Used in conjunction with 'install_dependencies'/'install_dependencies_develop'."
    )

    parser.add_argument(
        "--env", dest="environment", default=None,
        help="The target environment directory (e.g. 'env' or 'venv') to install the python package and its' dependencies into. Used in conjunction with 'install_dependencies'/'install_dependencies_develop'."
    )

    parser.add_argument(
        "--include_project", default=False, action="store_true",
        help="Includes a link to / installation of the project itself. Used in conjunction with 'install_dependencies'/'install_dependencies_develop'."
    )

    parser.add_argument(
        "--git_fp", default="git",
        help="The git executable file path."
    )

    result = parser.parse_args()
    return result


def _absolute_path( p ):
    return os.path.normpath(os.path.abspath(p))


if __name__ == "__main__":
    main()
