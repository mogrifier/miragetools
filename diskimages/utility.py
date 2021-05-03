# Utility functions needed for audio manipulation
import os
import sys


# For converting a 16 bit mono file in little-endian format to 8 bit.
WAVHEADER = 44

# TODO Should test for presence of WAV header rather than assume one.
# Flag could be used to determine if wav or raw output is desired.
# Write WAV header if user wants one.
# In the meantime, the Mirage only uses RAW data so that is what this provides.

def convert_16bitfile_folder_to_8bit(input_folder):
    # iterate the folder for .wav files and convert each
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".wav"):
            # convert. need path and file name
            print(f'converting {os.path.join(input_folder, filename)}')
            convert_16bitfile_to_8bit(os.path.join(input_folder, filename))
        else:
            continue


def convert_16bitfile_to_8bit(input_file):
    input = read_file_bytes(input_file)
    output = convert_16_to_8bit(input)
    # write output to a new file
    name_stub = os.path.basename(input_file)
    write_file(output, "8bit-" + name_stub)

def convert_16_to_8bit (input):
    input_length = len(input)
    # length of 8 bit with no header.
    eightbit_length = (int)((input_length - WAVHEADER) / 2)
    converted = bytearray(eightbit_length)
    # little-endian data means data is stored little end (LSB) first.
    # Skip 44 byte wavheader and start on MSB (2nd byte)
    index = 0
    for x in range(45, input_length, 2):
        # why 45? zero-based. skipping 0-43, then 44 (LSB). 45 is first MSB.
        converted[index] = input[x]
        index += 1
    print(f'output file length = {len(converted)}')
    return converted

def read_file_bytes(sample_file):
    samples = open(os.path.join(sys.path[0], sample_file), 'rb')
    data = bytearray(samples.read())
    print(f'info: data read from source file = {len(data)}.')
    return data


def write_file(data, name):
    output = open(name, 'wb')
    output.write(data)
    output.close()
    print(f'wrote file {name}')


if __name__ == '__main__':
    # pass file name argument
    convert_16bitfile_to_8bit("/Users/eizdepski/rawpcm16bitmono.raw")

    convert_16bitfile_folder_to_8bit("/Users/eizdepski/PycharmProjects/WaveSynUI/resources/com/erichizdepski/wavetable")
