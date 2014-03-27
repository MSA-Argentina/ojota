from unittest.case import TestCase

from ojota import Ojota, current_data_code, set_data_source, sources


class FunctionsTest(TestCase):
    def test_data_code(self):
        """Testing the current_data_code function."""
        expected = "data_code_1"
        current_data_code(expected)
        result = Ojota.get_current_data_code()
        self.assertEqual(expected, result)

    def test_data_source(self):
        """Testing the set_data_source function."""
        expected = "dir1/dir2"
        set_data_source(expected)
        result = sources._DATA_SOURCE
        self.assertEqual(expected, result)
