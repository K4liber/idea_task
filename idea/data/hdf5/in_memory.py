from collections import defaultdict
from typing import Dict, Set, Tuple

import h5py
from sklearn.cluster import KMeans

from .utils import TABLE_TO_EXTRACTOR, get_table_df, CLUSTER_COL_NAME
from ..interface import DatabaseInterface
from ..entities import Node, Generator, Branch
from ...utils import logger


class InMemory(DatabaseInterface):
    def __init__(self, hdf5_filepath: str):
        self._data = dict()

        for table_name in TABLE_TO_EXTRACTOR:
            self._data[table_name] = defaultdict(dict)

        with h5py.File(hdf5_filepath, "r") as file:
            self._load_entities_from_hdf5_file(file)
            self._branches_df = get_table_df(file, 'branches', ['node_from', 'node_to', 'flow'])

    def get_hour_to_nodes(self, hours: Set[int] = None) -> Dict[int, Dict[int, Node]]:
        return self._get_hours_data(hours, 'nodes')

    def get_hour_to_gens(self, hours: Set[int] = None) -> Dict[int, Dict[int, Generator]]:
        return self._get_hours_data(hours, 'gens')

    def get_hour_to_branches(self, hours: Set[int] = None) -> Dict[int, Dict[Tuple[int, int], Branch]]:
        return self._get_hours_data(hours, 'branches')

    # This is the simplest clustering implementation.
    # Clustering use only the flow column and the KMeans algorithm.
    def get_branch_to_cluster(self, n_clusters: int, hours: Set[int] = None) -> Dict[Tuple[int, int], int]:
        branches_in_hours = self._branches_df.loc[self._branches_df['hour'].isin(hours)]
        branches_avg = branches_in_hours.abs().groupby(['node_from', 'node_to']).mean()
        # Clustering settings
        columns = ['flow']  # Which columns use for clustering
        algorithm = KMeans(n_clusters=n_clusters)
        clusters = algorithm.fit_predict(branches_avg[columns])
        branches_avg[CLUSTER_COL_NAME] = clusters
        branch_to_cluster = dict()

        for _, row in branches_avg.iterrows():
            branch_to_cluster[(abs(int(row.name[0])), abs(int(row.name[1])))] = int(row['cluster'])

        return branch_to_cluster

    def _load_entities_from_hdf5_file(self, file):
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
