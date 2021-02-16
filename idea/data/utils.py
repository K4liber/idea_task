from enum import Enum
from os import listdir, getcwd
from os.path import isfile, join
from typing import List


TABLE_NAMES = [
    'nodes',
    'branches',
    'gens'
]


def load_files_paths(main_dir: str, ext: str = '') -> List[str]:
    if not main_dir.startswith('/'):
        main_dir = join(getcwd(), main_dir)

    files_paths = [join(main_dir, f) for f in listdir(main_dir) if isfile(join(main_dir, f))]

    if ext == '':
        return files_paths
    else:
        return [f for f in files_paths if f.endswith(ext)]
