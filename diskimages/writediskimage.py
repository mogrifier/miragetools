'''
This utility will read a disk image file and using it as a template, create a
new disk image loaded with arbitrary sample data. Ideally, the data would come
from really good looping samples, like single cycle waveforms. The Mirage can
use multisamples, so up to 8 waveforms for each block of 64KB can be used.
'''
import sys
import os.path

import utility


def create_disk_image(sample_source, output_file):
    template = read_template_disk_image()
    new_wavesamples = read_sample_source(sample_source)
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
    utility.write_file(new_image, output_file + ".img")

    # verify
    utility.verify_image(new_image)

# This file needs to be written to a floppy disk for use in the Mirage, or
# converted to a format used with a USB drive.
# name is the disk image file to write to.
# samples are the 6 bytearrays (64KB each) being written into the image file template.


def write_wave_sample(samples, name):
    output = open(name, 'wb')
    output.write(samples)
    output.close()
    print(f'wrote file {name}')

# Read the mirage disk for use as a template file. This is important since the disk should have the OS on it plus
# the parameter data for the samples being written. Those can be changed later using the Mirage, but are needed
# initially.


def read_template_disk_image():
    disk_image_template = open(os.path.join(sys.path[0], 'MELSET1'), 'rb')
    mirage_data = bytearray(disk_image_template.read())
    print(f'info: data read from template disk image = {len(mirage_data)}.')
    return mirage_data


def read_sample_source(sample_file):
    # sys.path[0] is where script is running
    samples = open(os.path.join(sys.path[0], sample_file), 'rb')
    data = bytearray(samples.read())
    print(f'info: data read from sample source = {len(data)}.')
    return data

# Return a random byte array.


def create_dummy_data():
    # just make a 64KB random data array
    return bytearray(os.urandom(65536))


if __name__ == '__main__':
    # read and pass file name argument
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
    if len(sys.argv) != 3:
        print("A sample source file name and output file name (for new disk image) is required. Exiting.")
        sys.exit(1)
    else:
        create_disk_image(sys.argv[1], sys.argv[2])
