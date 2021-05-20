import unittest
from diskimages import utility


class UtilityTestCase(unittest.TestCase):

    def test_remove_wavheader(self):
        data = bytearray(100)
        # testing a static method
        no_header = utility.remove_waveheader(data)
        # method removes 44 bytes from array
        self.assertEqual(len(no_header), 56)

    def test_dummy_data(self):
        data = bytearray(utility.create_dummy_data())
        self.assertEqual(len(data), 65536)


if __name__ == '__main__':
    unittest.main()
