from os.path import join
from unittest import TestCase

from ...data.utils import load_files_paths
from ...definitions import ROOT_DIR


class TestLoadFilesPaths(TestCase):
    def test_existing_path(self):
        got = load_files_paths(join(ROOT_DIR, 'data/hdf5/files/'), 'hdf5')
        want = [join(ROOT_DIR, 'data/hdf5/files/', 'task_data.hdf5')]
        self.assertTrue(set(got).intersection(set(want)) == set(got), 'files paths want=%s, got=%s' % (want, got))
