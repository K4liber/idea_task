from os.path import join
from unittest import TestCase

from ...data.in_memory import DatabaseInMemory
from ...data.entities import Node
from ...definitions import ROOT_DIR


class TestDatabaseInMemory(TestCase):
    def setUp(self) -> None:
        hd5_files_dir = join(ROOT_DIR, 'data/hd5/files/')  # TODO prepare folder with some testing, mocked data
        self.db = DatabaseInMemory(hd5_files_dir)

    def test_get_nodes(self):
        nodes_first_hour = self.db.get_hour_to_nodes({1})
        self.assertTrue(1 in nodes_first_hour, 'nodes dict should have one element with key=1')
        first_node = Node(1, 1, 0.0)
        self.assertTrue(nodes_first_hour[1][1] == first_node,
                        'there should be a node 1 with values %s' % first_node)

    def test_get_branches(self):
        branches_first_hour = self.db.get_hour_to_branches({1})
        self.assertTrue(1 in branches_first_hour, 'branches dict should have one element with key=1')
        self.assertTrue(tuple([2, 1]) in branches_first_hour[1], 'there should be a branch between 2 and 1 nodes')

    def test_get_gens(self):
        gens = self.db.get_hour_to_gens()
        self.assertTrue(1 in gens, 'gens dict should have element with key=1')
        self.assertTrue(len(gens) == 24, 'branches dict should have one element with key=1')
