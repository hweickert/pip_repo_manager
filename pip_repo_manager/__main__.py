import argparse

from . _pip_repo_manager import PipRepoManager



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
        pip_repo_manager.install_dependencies( args.project_path, args.root_directory )

    elif args.command == "install_dependencies_develop":
        if args.project_path is None:
            raise ValueError( "'--project_path' must be set when using the 'install_dependencies_develop' command." )
        pip_repo_manager.install_dependencies_develop( args.project_path, args.root_directory )

    elif args.command == "index":
        pip_repo_manager.create_index_html()

    elif args.command == "git_status":
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
        "command", choices=["index", "create_wheel", "install_dependencies_develop", "install_dependencies", "git_status", "git_gui", "git_pull_origin"], default="index", type=unicode,
        help="What command to execute."
    )

    parser.add_argument(
        "root_directory",
        help="The directory that contains all the python package repositories." )

    parser.add_argument(
        "--project", default=None,
        help="The project to work on. Used in conjunction with 'create_wheel'." )

    parser.add_argument(
        "--project_path", default=None,
        help="The project path to work on. Used in conjunction with 'install_develop'." )

    parser.add_argument(
        "--git_fp", default="git",
        help="The git executable file path."
    )

    result = parser.parse_args()
    return result



if __name__ == "__main__":
    main()
