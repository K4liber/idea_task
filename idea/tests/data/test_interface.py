from unittest import TestCase

from ...data.in_memory import DatabaseInMemory
from ...data.interface import DatabaseInterface


class TestInterface(TestCase):
    def test_is_subclass(self):
        implementations = [
            DatabaseInMemory
        ]

        for implementation in implementations:
            self.assertTrue(issubclass(implementation, DatabaseInterface), 'implementation error')
