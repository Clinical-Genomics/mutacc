from pathlib import Path
import os
import gzip
def parse_path(path, file_type: str  = 'file'):

    path = Path(path).expanduser().absolute()

    if file_type not in ['file', 'dir']:

        raise Exception("argument 'type' must be 'file' or 'dir'")

    if file_type == 'file':

        if not path.is_file():

            raise IOError("not a valid file: %s" % (path))

    else:

        if not path.is_dir():

            raise IOError("not a valid directory: %s" % (path))

    return path

def make_dir(path):

    path = Path(path).expanduser().absolute()

    if not path.is_dir():

        path.mkdir(parents=True, exist_ok=True)

    return path

def get_file_handle(file_name):

    file_name = parse_path(file_name)


    if file_name.name.endswith('.gz'):

        return gzip.open(file_name, 'rt')

    else:

        return open(file_name, 'r')

def list_files(directory):

    directory_path = parse_path(directory, file_type='dir')
    for file in os.listdir(directory_path):
        file_path = directory_path.joinpath(file)
        if file_path.is_file():
            yield file_path

def list_dirs(directory):

    directory_path = parse_path(directory, file_type='dir')
    for dir in os.listdir(directory_path):
        dir_path = directory_path.joinpath(dir)
        if dir_path.is_dir():
            yield dir_path
