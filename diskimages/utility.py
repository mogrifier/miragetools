# Utility functions needed for audio manipulation
import hashlib
import os
import sys

# Global variables
WAVHEADER = 44
TRACK_LENGTH = 5632


# TODO Should check for presence of WAV header rather than assume one.
# Flag could be used to determine if wav or raw output is desired.
# Write WAV header if user wants one.
# In the meantime, the Mirage only uses RAW data so that is what this provides.


def remove_waveheader(data):
    # return data (bytearray) without 44 byte header
    return data[44: len(data)]


def write_file(data, name):
    output = open(name, 'wb')
    output.write(data)
    output.close()
    print(f'wrote file {name}')


# Read from the current working directory or an optional root directory.


def read_file_bytes(sample_file, root):
    if root is None:
        samples = open(os.path.join(sys.path[0], sample_file), 'rb')
        data = bytearray(samples.read())
        print(f'info: data read from source file = {len(data)}.')
        return data
    else:
        samples = open(os.path.join(root, sample_file), 'rb')
        data = bytearray(samples.read())
        print(f'info: data read from source file = {len(data)}.')
        return data


# Operates on bytearrays and converts 16 to 8 bit. This assumes little-endian byte order.
# FIXME assumes a wav (riff) file header. Need to test for this instead.

def convert_16_to_8bit(input_bytes):
    input_length = len(input_bytes)
    # length of 8 bit with no header.
    eightbit_length = (int)((input_length - WAVHEADER) / 2)
    converted = bytearray(eightbit_length)
    # little-endian data means data is stored little end (LSB) first.
    # Skip 44 byte wavheader and start on MSB (2nd byte)
    index = 0
    for x in range(45, input_length, 2):
        # why 45? zero-based. skipping 0-43, then 44 (LSB). 45 is first MSB.
        converted[index] = input_bytes[x]
        index += 1
    print(f'output file length = {len(converted)}')
    return converted


def convert_16bitfile_to_8bit(input_file):
    input_bytes = read_file_bytes(input_file)
    output = convert_16_to_8bit(input_bytes)
    # write output to a new file
    name_stub = os.path.basename(input_file)
    write_file(output, "8bit-" + name_stub)


def convert_16bitfile_folder_to_8bit(input_folder):
    # iterate the folder for .wav files and convert each
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".wav"):
            # convert. need path and file name
            print(f'converting {os.path.join(input_folder, filename)}')
            convert_16bitfile_to_8bit(os.path.join(input_folder, filename))
        else:
            continue


# each block of data includes the wavesample data plus 512 byte chunks
# interspersed between mirage disk tracks. This will remove the extra
# data, returning just the wavesample data (64KB).


def collapse_wave_data(samples):
    clean_wavesample = bytearray(66560)
    wave_data = 5120
    skip_data = 512

    for start in range(13):
        end = start * wave_data + wave_data
        print(f"copying bytes {start * TRACK_LENGTH}:{start * TRACK_LENGTH + wave_data}")
        print(f"to {start * wave_data}:{end}")
        clean_wavesample[start * wave_data:end] = \
            samples[start * TRACK_LENGTH:start * TRACK_LENGTH + wave_data]

    # skip first 1024 bytes of parameter data
    return clean_wavesample[1024:66560]


# Take a full image bytearray and verify the wave samples in each upper/lower pair are identical.
# Read each chunk of data and compare. Could use checksum to avoid brute force method.
# Only works if upper and lower are the same.


def verify_image(data):
    # chunk to collapse_wave_data and do checksum. Compare with next chunk. And so.
    sample_metadata = {2, 15, 28, 41, 54, 67}
    lower1 = bytearray(73216)
    lower1_start = 2 * 5632
    lower1[0:73215] = data[lower1_start: lower1_start + 73216]
    lower1 = collapse_wave_data(lower1)
    # do checksum
    lower1_md5 = hashlib.md5(lower1)
    print(f'first checksum = {lower1_md5.hexdigest()}')

    lower2 = bytearray(73216)
    lower2_start = 15 * 5632
    lower2[0:73215] = data[lower2_start: lower2_start + 73216]
    lower2 = collapse_wave_data(lower2)
    # do checksum
    lower2_md5 = hashlib.md5(lower2)
    print(f'second checksum = {lower2_md5.hexdigest()}')


# Return a random byte array.


def create_dummy_data():
    # just make a 64KB random data array
    return bytearray(os.urandom(65536))


if __name__ == '__main__':
    # pass file name argument
    # convert_16bitfile_to_8bit("/Users/eizdepski/rawpcm16bitmono.raw")

    convert_16bitfile_folder_to_8bit("E:\\java_work\\WaveSynUI\\resources\\com\\erichizdepski\\wavetable")
