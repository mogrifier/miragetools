"""
This utility will read a disk image file and using it as a template, create a
new disk image loaded with arbitrary sample data. Ideally, the data would come
from really good looping samples, like single cycle waveforms. The Mirage can
use multisamples, so up to 8 waveforms for each block of 64KB can be used.
"""

import configparser
import logging
import os.path
import sys

from pathlib import Path
from sys import platform

from diskimages import utility

APP = "wavsyn"


class MirageDiskManager:
    fairlight_template = 'templates\\fairlight_template.img'
    app_root = None
    mirage_ready = None
    hfe = None
    intermediate_wav = None
    wavetables = None
    fairlight = None
    k3 = None
    home = os.getenv("HOMEPATH")
    logfile = None

    # init method
    def __init__(self):
        if platform == "linux" or platform == "linux2" or platform == "darwin":
            # linux
            self.home = os.getenv("HOME")
        # windows HOMEPATH is the default
        # read config file parameters needed
        config = configparser.ConfigParser()
        config.read("C:\\Users\\eizde\\PycharmProjects\\pythonProject\\settings" + os.path.sep + "config.ini")
        # set variables
        if config['FILES']['HOME']:
            self.home = config['FILES']['HOME']
        # need an app_root directory
        self.app_root = self.home + os.path.sep + APP
        if not os.path.exists(self.app_root):
            os.makedirs(self.app_root)
        # logging
        self.logfile = self.app_root + os.path.sep + config['LOGS']['LOGFILE']
        logging.basicConfig(filename=self.logfile, level=config['LOGS']['LEVEL'])
        self.mirage_ready = config['FILES']['OUTPUT_DISK_IMAGE_FOLDER']
        self.hfe = config['FILES']['OUTPUT_HFE_FOLDER']
        self.intermediate_wav = config['FILES']['INTERMEDIATE_WAV_FOLDER']
        self.wavetables = config['FILES']['WAVETABLES']
        self.fairlight = config['FILES']['FAIRLIGHT']
        self.k3 = config['FILES']['KAWAIK3']
        self.mirage_sounds = config['FILES']['MIRAGE_SOUNDS']
        if not os.path.exists(self.app_root + os.path.sep + self.mirage_ready):
            os.makedirs(self.app_root + os.path.sep + self.mirage_ready)
        if not os.path.exists(self.app_root + os.path.sep + self.hfe):
            os.makedirs(self.app_root + os.path.sep + self.hfe)
        if not os.path.exists(self.app_root + os.path.sep + self.intermediate_wav):
            os.makedirs(self.app_root + os.path.sep + self.intermediate_wav)
        if not os.path.exists(self.app_root + os.path.sep + self.wavetables):
            os.makedirs(self.app_root + os.path.sep + self.wavetables)
        if not os.path.exists(self.app_root + os.path.sep + self.fairlight):
            os.makedirs(self.app_root + os.path.sep + self.fairlight)
        if not os.path.exists(self.app_root + os.path.sep + self.k3):
            os.makedirs(self.app_root + os.path.sep + self.k3)
        if not os.path.exists(self.app_root + os.path.sep + self.mirage_sounds):
            os.makedirs(self.app_root + os.path.sep + self.mirage_sounds)
        logging.info("initialized application from settings/config.ini")
        logging.info("application output directory is " + self.app_root)

    # Reads a file from INTERMEDIATE_WAV_FOLDER defined in config.ini and writes it to a mirage disk image format
    # using a template to insert the data in. The template contains the Mirage OS, sound parameters, wavetable
    # settings, and global mirage config parameters.

    def create_disk_image(self, sample_source, output_file):
        template = self.read_template_disk_image(self.fairlight_template)
        new_wavesamples = self.read_sample_source(sample_source)
        # copy the template byte data to the new disk image
        new_image = bytearray(len(template))
        new_image[0:len(template)] = template[0:len(template)]

        # go through the tracks/sectors and write data. copy template to the new_image as you go.
        track_length = 5632
        # wavesample plus extra data size
        sample_size = 72704
        # track start number for wave samples
        sample_metadata = {2, 15, 28, 41, 54, 67}
        # each wavesample start at the given track PLUS 1024 bytes

        # write 78 sectors worth of data (6 * 64KB) into the 5120 byte slots in the template
        for count in range(6):
            for x in range(13):
                track = (count * 13) + x + 2
                position = track * track_length
                wavesample_position = count * 65536 + x * 5120
                if x == 0:
                    # skip 1024 and copy 4096 for first sector of each sample.
                    wavesample_position = count * 65536
                    new_image[position + 1024:position + 5120] = \
                        new_wavesamples[wavesample_position:wavesample_position + 4096]
                else:
                    wavesample_position = count * 65536 + 4096 + (x - 1) * 5120
                    new_image[position:position + 5120] = \
                        new_wavesamples[wavesample_position:wavesample_position + 5120]
            print(f'info: wrote wave sample {count + 1}')
        # save the new disk image
        utility.write_file(new_image, "mirage_ready\\" + output_file + ".img")

        # verify
        utility.verify_image(new_image)

    # This file needs to be written to a floppy disk for use in the Mirage, or
    # converted to a format used with a USB drive.
    # name is the disk image file to write to.
    # samples are the 6 bytearrays (64KB each) being written into the image file template.
    # Writes to the INTERMEDIATE_WAV_FOLDER defined in config.ini.

    def write_wave_sample(self, samples, name):
        output = open(self.app_root + os.path.sep + self.intermediate_wav + os.path.sep + name, 'wb')
        output.write(samples)
        output.close()
        logging.info(f'wrote file {self.intermediate_wav + os.path.sep + name}')

    # Read the mirage disk for use as a template file. This is important since the disk should have the OS on it plus
    # the parameter data for the samples being written. Those can be changed later using the Mirage, but are needed
    # initially.

    def read_template_disk_image(self, template):
        disk_image_template = open(os.path.join(sys.path[0], template), 'rb')
        mirage_data = bytearray(disk_image_template.read())
        print(f'info: data read from template disk image = {len(mirage_data)}.')
        return mirage_data

    def read_sample_source(self, sample_file):
        input_source = self.app_root + os.path.sep + self.intermediate_wav + os.path.sep + sample_file
        samples = open(input_source, 'rb')
        data = bytearray(samples.read())
        logging.info(f'data read from {input_source} = {len(data)}.')
        samples.close()
        return data

    # This will extract the data from a mirage disk image (original, not hfe) in MIRAGE_READY from config.ini.
    # and write it out as 6 wavesample files. They are raw pcm data (no wav header). Format is:
    # mono, unsigned 8 bit, little-endian

    def extract_wavesamples(self, filename):
        logging.info(f"processing file {filename}")
        name_stub = os.path.splitext(filename)[0]
        # create six separate arrays of binary data, each initially 72704 bytes.
        # This contains the 64KB wavesample plus extra 512 byte sectors
        # and initial 1024 byte parameter data to be removed.
        mirage_disk = open(self.app_root + os.path.sep + self.mirage_ready + os.path.sep + filename, 'rb')
        mirage_data = bytearray(mirage_disk.read())
        logging.info(f'data read = {len(mirage_data)}.')
        mirage_disk.close()

        # wavesample plus extra data size
        sample_size = 72704
        # calculate offset and remove short sectors
        # lower half wavesample 1, starts at sector 2 (skips 0 and 1)
        track_length = 5632
        # track start number for samples
        sample_metadata = {name_stub + "_lh1.wav": 2, name_stub + "_uh1.wav": 15,
                           name_stub + "_lh2.wav": 28, name_stub + "_uh2.wav": 41,
                           name_stub + "_lh3.wav": 54, name_stub + "_uh3.wav": 67}

        for name, track in sample_metadata.items():
            # create a new byte array containing correct data (64KB chunk)
            offset = track * track_length
            data = bytearray(mirage_data[offset:offset + sample_size])
            logging.info(f"***** processing {name} *****")
            wavesample = utility.collapse_wave_data(data)
            self.write_mirage_sound(wavesample, name)

    # Write a 64KB wave file. File is mono, 8bit unsigned PCM. Sample rate is unknown, but
    # default is 29411Hz, so the sample is about 2 seconds long. To get the actual sample rate,
    # you need to know how to read the parameter data from the disk and what it means.

    def write_mirage_sound(self, samples, name):
        output = open(self.app_root + os.path.sep + self.mirage_sounds + os.path.sep + name, 'wb')
        output.write(samples)
        output.close()


if __name__ == '__main__':
    # read and pass file name argument

    mirage = MirageDiskManager()
    mirage.create_disk_image("1st_24.wav", "1st_24")
    mirage.create_disk_image("2nd_24.wav", "2nd_24")
    mirage.create_disk_image("3rd_24.wav", "3rd_24")
    mirage.create_disk_image("4th_24.wav", "4th_24")
    mirage.create_disk_image("5th_24.wav", "5th_24")
    exit(0)
    # mirage.create_disk_image("virus_ti.wav", "virus_ti.img")


    print('''
    The sample source file must contain 6 64KB chunks of data, organized in this order:
    lower half 1
    upper half 1
    lower half 2
    upper half 2
    lower half 3
    upper half 3
    
    Of course you can load any data you like, any way you like, since not bound by Mirage sampling rules.
    ''')
    if len(sys.argv) == 3:
        create_disk_image(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        # my hack to process some ppg files; voices-image.wav voices
        mirage.create_disk_image("1st_24.wav", "1st_24")
        mirage.create_disk_image("2nd_24.wav", "2nd_24")
        mirage.create_disk_image("3rd_24.wav", "3rd_24")
        mirage.create_disk_image("4th_24.wav", "4th_24")
        mirage.create_disk_image("5th_24.wav", "5th_24")

    else:
        path = Path(sys.argv[0])
        root_directory = os.path.join(path.parent.absolute(), "fairlight")
        root = os.listdir(root_directory)
        print(f'root directory = {root}')
        for item in root:
            print(f'processing {item}')
            create_disk_image(os.path.join(root_directory, item), item)

        # print("A sample source file name and output file name (for new disk image) is required. Exiting.")
        # sys.exit(1)
