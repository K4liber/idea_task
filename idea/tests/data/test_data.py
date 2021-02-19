from os.path import join
from unittest import TestCase

import h5py

from ...data.utils import load_files_paths
from ...definitions import ROOT_DIR
from ...utils.logger import logger
import numpy as np
import pandas as pd


class TestData(TestCase):
    def test_data_exploration(self):
        files_dir = join(ROOT_DIR, 'data/hd5/files/')
        hd5_files_paths = load_files_paths(files_dir, 'hdf5')
        branches_df = pd.DataFrame(columns=['node_from', 'node_to', 'flow', 'hour'], index=None)
        nodes_df = pd.DataFrame(columns=['node_id', 'node_type', 'demand', 'hour'], index=None)
        gens_df = pd.DataFrame(columns=['node_id', 'generation', 'cost', 'hour'], index=None)

        for filepath in hd5_files_paths:
            file = h5py.File(filepath)

            for hour in [x for x in file.values()][0]:
                try:
                    hour_int = int(hour.removeprefix('hour_'))
                except ValueError:
                    logger.error('wrong hour format=%s != hour_{int}' % hour)
                    continue
                # Fill branches df
                branches_hour_df = pd.DataFrame(columns=['node_from', 'node_to', 'flow'],
                                                data=np.array(h5py.File(filepath)['results/' + hour + '/branches']))
                branches_hour_df['hour'] = [hour_int for _ in range(len(branches_hour_df))]
                branches_df = branches_df.append(branches_hour_df, ignore_index=True)
                # Fill nodes df
                nodes_hour_df = pd.DataFrame(columns=['node_id', 'node_type', 'demand'],
                                             data=np.array(h5py.File(filepath)['results/' + hour + '/nodes']))
                nodes_hour_df['hour'] = [hour_int for _ in range(len(nodes_hour_df))]
                nodes_df = nodes_df.append(nodes_hour_df, ignore_index=True)
                # Fill gens df
                gens_hour_df = pd.DataFrame(columns=['node_id', 'generation', 'cost'],
                                            data=np.array(h5py.File(filepath)['results/' + hour + '/gens']))
                gens_hour_df['hour'] = [hour_int for _ in range(len(gens_hour_df))]
                gens_df = gens_df.append(gens_hour_df, ignore_index=True)

        gens_group_by_nodes = gens_df.groupby(['node_id']).agg('count')
        gens_nodes = gens_group_by_nodes.index.tolist()
        gens_hours_count = gens_group_by_nodes['hour'].tolist()
        # Check if all generator are available in all of the hours
        for i, gen_hours_count in enumerate(gens_hours_count):
            self.assertTrue(gen_hours_count == 24, 'gen %d is not present in all of the hours' % gens_nodes[i])
        # Check if generator have the same demand and generation for each hour
        for gen_node_id in gens_nodes:
            demands = nodes_df.loc[nodes_df['node_id'] == gen_node_id]['demand'].tolist()

            for demand in demands:
                self.assertTrue(demand == demands[0], 'generator do not have the same demand for each hour')

            generations = gens_df.loc[gens_df['node_id'] == gen_node_id]['generation'].tolist()

            for generation in generations:
                self.assertTrue(generation == generations[0], 'generator do not have the same generation for each hour')
