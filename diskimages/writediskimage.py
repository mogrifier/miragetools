'''
This utility will read a disk image file and using it as a template, create a
new disk image loaded with arbitrary sample data. Ideally, the data would come
from really good looping samples, like single cycle waveforms. The Mirage can
use multisamples, so up to 8 waveforms for each block of 64kb can be used.
'''
import sys
import os.path


def create_disk_image(sample_source, output_file):
    template = read_disk_image()
    dummy = create_dummy_data()
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

    # first sector is special
    position = 2 * track_length
    new_image[position + 1024:position + 5120] = dummy[0:4096]
    position = position + 5120
    new_image[position:position + 512] = template[position:position + 512]

    # write 78 sectors worth of data (6 * 64KB) into the 5120 byte slots in the template
    for count in range(6):
        for x in range(13):
            track = (count * 13) + x + 2
            position = track * track_length
            if x == 0:
                # skip 1024 and copy 4096
                new_image[position + 1024:position + 5120] = dummy[0:4096]
            else:
                new_image[position:position + 5120] = dummy[0:5120]

    # save the new disk image
    write_wave_sample(new_image, output_file)

# This file needs to be written to a floppy disk for use in the Mirage, or
# converted to a format used with a USB drive.
# name is the disk image file to write to.
# samples are the 6 bytearrays (64kb each) being written into the image file template.


def write_wave_sample(samples, name):
    output = open(name, 'wb')
    output.write(samples)

# Read the mirage disk for use as a template file. This is important since the disk should have the OS on it plus
# the parameter data for the samples being written. Those can be changed later using the Mirage, but are needed
# initially.


def read_disk_image():
    disk_image_template = open(os.path.join(sys.path[0], 'FULLMELL'), 'rb')
    mirage_data = bytearray(disk_image_template.read())
    print(f'data read = {len(mirage_data)}.')
    return mirage_data

# Return a random byte array.


def create_dummy_data():
    # just make a 64kb random data array
    return bytearray(os.urandom(65536))


if __name__ == '__main__':
    # read and pass file name argument
    if len(sys.argv) != 3:
        print("A sample source file name and output file name (for new disk image) is required. Exiting.")
        sys.exit(1)
    else:
        create_disk_image(sys.argv[1], sys.argv[2])
