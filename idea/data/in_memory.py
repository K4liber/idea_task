from collections import defaultdict
from typing import Dict, Set

import h5py

from .interface import DatabaseInterface
from .utils import load_files_paths, TABLE_NAMES
from ..utils import logger


class DatabaseInMemory(DatabaseInterface):
    def __init__(self, hd5_files_dir: str):
        self._data = dict()

        for table_name in TABLE_NAMES:
            self._data[table_name] = defaultdict(dict)

        hd5_files_paths = load_files_paths(hd5_files_dir, 'hdf5')
        # TODO refactor the code below to be more readable and editable
        # TODO maybe load the data directly to pandas data frame
        for hd5_filepath in hd5_files_paths:
            with h5py.File(hd5_filepath, "r") as f:
                hours_key = list(f.keys())[0]

                for hour, hour_row in f[hours_key].items():
                    try:
                        hour_int = int(hour.removeprefix('hour_'))
                    except ValueError:
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
                                self._data['branches'][hour_int][key] = flow
                        if table_name == 'nodes':
                            for value in values:
                                if len(value) != 3:
                                    logger.error('value in nodes table have wrong number of elements 3!=%d'
                                                 % len(values))
                                    continue

                                try:
                                    node_id = int(value[0])
                                    properties = [int(value[1]), value[2]]
                                except ValueError as ve:
                                    logger.error(ve)
                                    continue

                                self._data['nodes'][hour_int][node_id] = properties
                        if table_name == 'gens':
                            for value in values:
                                if len(value) != 3:
                                    logger.error('value in branches table have wrong number of elements 3!=%d'
                                                 % len(values))
                                    continue

                                try:
                                    node_id = int(value[0])
                                except ValueError as ve:
                                    logger.error(ve)
                                    continue

                                properties = [value[1], value[2]]
                                self._data['gens'][hour_int][node_id] = properties
                        else:
                            logger.warning('unknown table name=%s' % table_name)

    def get_nodes(self, hours: Set[int] = None) -> Dict[int, dict]:
        return self._get_hours_data(hours, 'nodes')

    def get_gens(self, hours: Set[int] = None) -> Dict[int, dict]:
        return self._get_hours_data(hours, 'gens')

    def get_branches(self, hours: Set[int] = None) -> Dict[int, dict]:
        return self._get_hours_data(hours, 'branches')

    def _get_hours_data(self, hours: Set[int], table_name):
        if hours is None:
            return self._data[table_name]
        else:
            return {hour: branches for hour, branches in self._data[table_name].items() if hour in hours}
