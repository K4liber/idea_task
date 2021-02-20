from collections import defaultdict
from typing import Dict, Set, Tuple

import h5py

from idea.data.hdf5.utils import TABLE_TO_EXTRACTOR
from idea.data.interface import DatabaseInterface
from idea.data.entities import Node, Generator, Branch
from idea.utils import logger


class InMemory(DatabaseInterface):
    def __init__(self, hdf5_filepath: str):
        self._data = dict()

        for table_name in TABLE_TO_EXTRACTOR:
            self._data[table_name] = defaultdict(dict)

        with h5py.File(hdf5_filepath, "r") as file:
            self._load_data_from_hdf5_file(file)

    def get_hour_to_nodes(self, hours: Set[int] = None) -> Dict[int, Dict[int, Node]]:
        return self._get_hours_data(hours, 'nodes')

    def get_hour_to_gens(self, hours: Set[int] = None) -> Dict[int, Dict[int, Generator]]:
        return self._get_hours_data(hours, 'gens')

    def get_hour_to_branches(self, hours: Set[int] = None) -> Dict[int, Dict[Tuple[int, int], Branch]]:
        return self._get_hours_data(hours, 'branches')

    def _load_data_from_hdf5_file(self, file):
        hours_key = list(file.keys())[0]

        for hour, hour_row in file[hours_key].items():
            try:
                hour_int = int(hour.removeprefix('hour_'))
            except ValueError:
                logger.error('wrong hour format=%s != hour_{int}' % hour)
                continue

            for table_name, rows in hour_row.items():
                if table_name not in TABLE_TO_EXTRACTOR:
                    logger.warning('unknown table name=%s' % table_name)

                self._data[table_name][hour_int].update(
                    {e.get_id(): e for e in [TABLE_TO_EXTRACTOR[table_name](columns) for columns in rows]}
                )

    def _get_hours_data(self, hours: Set[int], table_name):
        if hours is None:
            return self._data[table_name]
        else:
            return {hour: records for hour, records in self._data[table_name].items() if hour in hours}
