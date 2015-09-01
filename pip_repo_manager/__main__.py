import argparse

from . _pip_repo_manager import PipRepoManager



def main():
    parser = argparse.ArgumentParser(description='PipRepoManager.')
    parser.add_argument( "command", default="index", type=unicode, choices=["index", "create_wheel", "git_status", "git_gui", "git_pull_origin"], help="What command to execute." )
    parser.add_argument( "root_directory",                                                            help="The directory that contains all the python packages (later used with 'pip install ... --find-links <<root_directory>>')." )
    parser.add_argument( "--project", default=None,                                                   help="The project to work on. Used in conjunction with 'create_wheel'." )
    parser.add_argument( "--git_fp", default="git",                                               help="The git executable file path." )
    args = parser.parse_args()

    pip_repo_manager = PipRepoManager( args.root_directory, args.git_fp )

    if args.command == "create_wheel":
        if args.project is None:
            raise ValueError( "'--project' must be set when using the 'create_wheel' command." )
        pip_repo_manager.create_wheel( args.project )

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



if __name__ == "__main__":
    main()
