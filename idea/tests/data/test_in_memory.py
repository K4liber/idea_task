from os.path import join
from unittest import TestCase

from ...data.in_memory import DatabaseInMemory
from ...definitions import ROOT_DIR


class TestDatabaseInMemory(TestCase):
    def setUp(self) -> None:
        hd5_files_dir = join(ROOT_DIR, 'data/hd5/')  # TODO prepare folder with some testing, mocked data
        self.db = DatabaseInMemory(hd5_files_dir)

    def test_get_branches(self):
        branches_first_hour = self.db.get_branches({1})
        self.assertTrue(1 in branches_first_hour, 'branches dict should have one element with key=1')
        self.assertTrue(tuple([2, 1]) in branches_first_hour[1], 'there should be a branch between 2 and 1 nodes')
