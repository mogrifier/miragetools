import configparser
import os
import platform
import unittest

import diskimages.diskmanager
from diskimages.diskmanager import MirageDiskManager

home = os.getenv("HOMEPATH")


class ConfigTestCase(unittest.TestCase):
    def test_config(self):
        # spot check some config values
        writer = MirageDiskManager()
        # this is a test specific to my system since I want to use the F drive
        self.assertEqual(writer.app_root, "F:\wavsyn")
        self.assertIsNotNone(writer.intermediate_wav)
        self.assertIsNotNone(writer.logfile)

    def test_directories(self):
        # verify all directories created
        config = configparser.ConfigParser()
        config.read("settings" + os.path.sep + "config.ini")
        # set variables
        if config['FILES']['HOME']:
            self.home = config['FILES']['HOME']
        # need an app_root directory
        self.app_root = self.home + os.path.sep + diskimages.diskmanager.APP
        self.assertTrue(os.path.exists(self.app_root))
        self.mirage_ready = config['FILES']['OUTPUT_DISK_IMAGE_FOLDER']
        self.hfe = config['FILES']['OUTPUT_HFE_FOLDER']
        self.intermediate_wav = config['FILES']['INTERMEDIATE_WAV_FOLDER']
        self.wavetables = config['FILES']['WAVETABLES']
        self.fairlight = config['FILES']['FAIRLIGHT']
        self.k3 = config['FILES']['KAWAIK3']
        self.mirage_sounds = config['FILES']['MIRAGE_SOUNDS']
        self.assertTrue(os.path.exists(self.app_root + os.path.sep + self.mirage_ready))
        self.assertTrue(os.path.exists(self.app_root + os.path.sep + self.hfe))
        self.assertTrue(os.path.exists(self.app_root + os.path.sep + self.intermediate_wav))
        self.assertTrue(os.path.exists(self.app_root + os.path.sep + self.wavetables))
        self.assertTrue(os.path.exists(self.app_root + os.path.sep + self.fairlight))
        self.assertTrue(os.path.exists(self.app_root + os.path.sep + self.k3))
        self.assertTrue(os.path.exists(self.app_root + os.path.sep + self.mirage_sounds))


class FileWritingTestCase(unittest.TestCase):

    def test_write_read_wave_sample(self):
        mirage = MirageDiskManager()
        data = bytearray(100)
        testfile = "test.dat"
        mirage.write_wave_sample(data, testfile)
        # do a test read - another method??

        # reading a 384KB wav file
        data = mirage.read_sample_source("testdata.wav")
        self.assertEqual(len(data), 6 * 65536)

    def test_extraction(self):
        config = configparser.ConfigParser()
        config.read("settings" + os.path.sep + "config.ini")
        if platform == "linux" or platform == "linux2" or platform == "darwin":
            # linux
            self.home = os.getenv("HOME")
        if config['FILES']['HOME']:
            self.home = config['FILES']['HOME']
        self.app_root = self.home + os.path.sep + diskimages.diskmanager.APP
        self.mirage_sounds = config['FILES']['MIRAGE_SOUNDS']
        mirage = MirageDiskManager()
        testfile = "testimage.img"
        mirage.extract_wavesamples(testfile)
        # check that it wrote the 6 separate files to MIRAGE_SOUNDS
        listing = os.listdir(self.app_root + os.path.sep + self.mirage_sounds)
        # test for the 6 files
        files = ["testimage_lh1.wav", "testimage_lh2.wav", "testimage_lh3.wav",
                 "testimage_uh1.wav", "testimage_uh2.wav", "testimage_uh3.wav"]

        for file in files:
            self.assertTrue(file in listing)

        # delete
        for file in files:
            if os.path.exists(self.app_root + os.path.sep + self.mirage_sounds + os.path.sep + file):
                os.remove(self.app_root + os.path.sep + self.mirage_sounds + os.path.sep + file)

if __name__ == '__main__':
    unittest.main()
