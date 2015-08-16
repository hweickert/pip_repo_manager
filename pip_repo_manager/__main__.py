import argparse

from . _pip_repo_manager import PipRepoManager



def main():
    parser = argparse.ArgumentParser(description='PipRepoManager.')
    parser.add_argument( "root_directory", help="The directory that contains all the python packages (later used with 'pip install ... --find-links <<root_directory>>')." )
    args = parser.parse_args()

    pip_repo_manager = PipRepoManager( args.root_directory )
    pip_repo_manager.create_index_html()



if __name__ == "__main__":
    main()
