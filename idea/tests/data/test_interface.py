from unittest import TestCase

from idea.data.hdf5.in_memory import InMemory
from ...data.interface import DatabaseInterface


class TestInterface(TestCase):
    def test_is_subclass(self):
        implementations = [
            InMemory
        ]

        for implementation in implementations:
            self.assertTrue(issubclass(implementation, DatabaseInterface), 'implementation error')
