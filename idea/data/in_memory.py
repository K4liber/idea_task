from collections import defaultdict
from typing import Dict, Set, Tuple

import h5py

from .hd5.utils import values_to_node, values_to_gen, values_to_branch
from .interface import DatabaseInterface
from .entities import Node, Generator, Branch
from .utils import load_files_paths, TABLE_NAMES
from ..utils import logger


class DatabaseInMemory(DatabaseInterface):
    def __init__(self, hd5_files_dir: str):
        self._data = dict()

        for table_name in TABLE_NAMES:
            self._data[table_name] = defaultdict(dict)

        hd5_files_paths = load_files_paths(hd5_files_dir, 'hdf5')

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
                            for branch_values in values:
                                branch = values_to_branch(branch_values)

                                if branch is not None:
                                    self._data['branches'][hour_int][branch.get_key()] = branch

                        elif table_name == 'nodes':
                            for node_values in values:
                                node = values_to_node(node_values)

                                if node is not None:
                                    self._data['nodes'][hour_int][node.get_id()] = node

                        elif table_name == 'gens':
                            for gen_values in values:
                                gen = values_to_gen(gen_values)

                                if gen is not None:
                                    self._data['gens'][hour_int][gen.get_node_id()] = gen
                        else:
                            logger.warning('unknown table name=%s' % table_name)

    def get_hour_to_nodes(self, hours: Set[int] = None) -> Dict[int, Dict[int, Node]]:
        return self._get_hours_data(hours, 'nodes')

    def get_hour_to_gens(self, hours: Set[int] = None) -> Dict[int, Dict[int, Generator]]:
        return self._get_hours_data(hours, 'gens')

    def get_hour_to_branches(self, hours: Set[int] = None) -> Dict[int, Dict[Tuple[int, int], Branch]]:
        return self._get_hours_data(hours, 'branches')

    def _get_hours_data(self, hours: Set[int], table_name):
        if hours is None:
            return self._data[table_name]
        else:
            return {hour: records for hour, records in self._data[table_name].items() if hour in hours}
