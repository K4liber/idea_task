from os.path import join
from unittest import TestCase

import h5py

from ...data.hdf5.utils import get_table_df
from ...definitions import ROOT_DIR


class TestData(TestCase):
    def test_data_exploration(self):
        hd5_filepath = join(ROOT_DIR, 'data/hdf5/files/task_data.hdf5')
        file = h5py.File(hd5_filepath)
        nodes_df = get_table_df(file, 'nodes', ['node_id', 'node_type', 'demand'])
        gens_df = get_table_df(file, 'gens', ['node_id', 'generation', 'cost'])
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
