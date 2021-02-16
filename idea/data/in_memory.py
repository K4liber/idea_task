from collections import defaultdict
from typing import Dict, Set

import h5py

from .interface import DatabaseInterface
from .utils import load_files_paths
from ..utils import logger


class DatabaseInMemory(DatabaseInterface):
    def __init__(self, hd5_files_dir: str):
        self._nodes = defaultdict(dict)  # TODO load nodes
        self._branches = defaultdict(dict)
        self._gens = defaultdict(dict)  # TODO load gens
        hd5_files_paths = load_files_paths(hd5_files_dir, 'hdf5')

        for hd5_filepath in hd5_files_paths:
            with h5py.File(hd5_filepath, "r") as f:
                hours_key = list(f.keys())[0]

                for hour, hour_row in f[hours_key].items():
                    try:
                        hour_int = int(hour.removeprefix('hour_'))
                    except ValueError as va:
                        logger.error('wrong hour format=%s != hour_{int}' % hour)

                    for table_name, values in hour_row.items():
                        if table_name == 'branches':
                            for value in values:
                                if len(value) != 3:
                                    logger.error('value in branches table have wrong number of elements 3!=%d'
                                                 % len(values))
                                    continue

                                flow = value[2]

                                try:
                                    key_parts = [int(value[0]), int(value[1])]
                                except ValueError as ve:
                                    logger.error(ve)
                                    continue

                                key = tuple(key_parts) if flow >= 0 else tuple(key_parts.__reversed__())
                                self._branches[hour_int][key] = flow
                        else:
                            logger.warning('unknown table name=%s' % table_name)

    def get_nodes(self, hours: Set[int] = {}) -> Dict[int, dict]:
        pass

    def get_gens(self, hours: Set[int] = {}) -> Dict[int, dict]:
        pass

    def get_branches(self, hours: Set[int] = {}) -> Dict[int, dict]:
        if len(hours) == 0:
            return self._branches
        else:
            return {hour: branches for hour, branches in self._branches.items() if hour in hours}
