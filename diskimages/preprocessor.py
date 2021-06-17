# Preprocessing functions on raw PCM files to ensure they are in format
# expected by writediskimage.py. The format is a single PCM file containing
# 6 * 64KB chunks of 8bit, mono, pcm data. The routines in this file are highly
# specific. Add your own!
import os
import sys
import utility


# Convert 16 sample wavetables (16KB 8 bit files) to 6 * 64 chunks. Write
# the output file.
# Read in 3 files. Write each eight times so that each pair of lower and
# upper keys on Mirage has the sample 16 samples spread across it.


def wavetable16_to_sample_source(table1, table2, table3, name):
    # table 1,2,3 are file names of 8bit wavetable files.
    # name is the output file name
    tables = [table1, table2, table3]
    output = bytearray(6 * 65536)

    index = 0
    for item in tables:
        table = utility.read_file_bytes(item)
        print(f'preprocessing {item}')
        chunksize = len(table)
        for j in range(8):
            # write entire table each time
            output[index:index + chunksize] = table[0:chunksize]
            index += chunksize

    # will write to the disk_image directory. Should change this.
    utility.write_file(output, name)


# Convert 16 sample wavetables (16KB 8 bit files) to 6 * 64 chunks. Write
# the output file.
# Read in 24 files. Write each 1KB sample. Load it up!
# Inputs are the source directory and a output file name ending in .wav.
# Data is raw PCM- no wave header.


def wavetable16_to_1KB_sample_source(source, name):
    # table 1,2,3 are file names of 8bit wavetable files.
    # name is the output file name
    count = len(os.listdir(source))
    tables = os.listdir(source)[0:24]
    if count > 24:
        print(f"directory has {count} files. Only using first 24.")
    output = bytearray(6 * 65536)
    # read in 16KB chunks
    chunksize = 16384
    index = 0
    for item in tables:
        table = utility.read_file_bytes(item, source)
        print(f'preprocessing {item}')
        # write each table once
        output_start = index * chunksize
        output[output_start:output_start + chunksize] = table
        index += 1

    # will write to the disk_image directory. Should change this.
    utility.write_file(output, name)


# Convert 16 sample wavetables (16KB 8 bit files) to 6 * 64 chunks. Write
# the output file.
# Read in 3 files. Write each 1KB sample 4 times in a row.


def wavetable16_to_4KB_sample_source(table1, table2, table3, name):
    # table 1,2,3 are file names of 8bit wavetable files.
    # name is the output file name
    tables = [table1, table2, table3]
    output = bytearray(6 * 65536)

    index = 0
    count = 0
    for item in tables:
        table = utility.read_file_bytes(item)
        print(f'preprocessing {item}')
        chunksize = 1024
        # write each table twice (lower and upper half)
        for x in range(2):
            for j in range(16):
                # write each 1KB sample four times.
                for k in range(4):
                    sample_start = j * chunksize
                    sample = table[sample_start: sample_start + chunksize]
                    index = j * 4 + k
                    output_start = index * chunksize + count * 65536
                    output[output_start:output_start + chunksize] = sample

            count = count + 1

    # will write to the disk_image directory. Should change this.
    utility.write_file(output, name)


# Just write all samples to disk in order. No spanning whole keyboard. Can do that
# in sound editing anyway on the Mirage.
# Write a directory of 16KB fairlight samples (8 bit, 30200Hz, unsigned) to a file for
# processing into the mirage format.
# Take a directory of Fairlight IIX wav files and convert to
# multiple 6 * 64KB sample source files for writing as a mirage image
# disk.

def write_fairlight_directory_to_intermediate_wav(src_folder, image_name):
    # get all file names in input directory. Use them all. Just stop when you run out.
    source_files = os.listdir(src_folder)
    print(source_files)
    print(f'copying {len(source_files)} samples to image')
    name = os.path.basename(src_folder)
    # take files 12 at a time (3 sounds, 4 samples per sound) and write a disk image
    file_count = len(source_files)
    if file_count > 24:
        # can only write a max of 24 files
        source_files = source_files[0:24]
        print(f"can't write all files. skipping {source_files[24:]}")
    # check for remainder and print out what is missing
    output = bytearray(6 * 65536)
    index = 0
    for item in source_files:
        sample = utility.read_file_bytes(item, src_folder)
        # remove wav header
        sample = utility.remove_waveheader(sample)
        print(f'preprocessing {item}')
        # should be 16384
        chunksize = len(sample)
        if chunksize != 16384:
            # pad to 16384
            raise ValueError("Sample size is not 16384")
        # write entire 16KB sample
        output[index:index + chunksize] = sample[0:chunksize]
        index += chunksize

    # will write to the disk_image directory. Should change this.
    utility.write_file(output, os.path.join("intermediate_wav",  image_name))


def write_virus_directory_to_intermediate_wav(src_folder, image_name):
    # get all file names in input directory. Use them all. Just stop when you run out.
    source_files = os.listdir(src_folder)
    print(source_files)
    print(f'copying {len(source_files)} samples to image')
    output = bytearray(6 * 65536)
    index = 0
    # write each 3 times so all 3 sounds are the same
    for x in range(3):
        for item in source_files:
            sample = utility.read_file_bytes(item, src_folder)
            print(f'preprocessing {item}')
            chunksize = 2048
            # write entire 2KB sample
            output[index:index + chunksize] = sample[0:chunksize]
            index += chunksize

    # FIXME will write to proper wavsyn directory using config.ini
    utility.write_file(output, os.path.join("intermediate_wav",  image_name))



def bulk_process_virus():
    root = "F:\\wavsyn\\virusT1\\Virus Classic Waveforms"
    tables = os.listdir(root)
    for file in tables:
        data = utility.read_file_bytes(file, root)
        #skip 100 byte header and convert
        eights = utility.convert_32bf_to_8bit(data[100:])
        utility.write_file(eights, (os.path.splitext(file)[0] + "_8bit.wav").replace(' ', '_'))



def bulk_process_ppg_tables():
    file_stub = "8bit-PPG_WA"
    for x in range(12, 31, 3):

        zero = ""
        if x < 10:
            zero = "0"
        file1 = file_stub + zero + str(x) + ".wav"
        file2 = file_stub + zero + str(x + 1) + ".wav"
        file3 = file_stub + zero + str(x + 2) + ".wav"

        wavetable16_to_4KB_sample_source(file1, file2, file3, "ppg" + str(x) + "-image.wav")


if __name__ == '__main__':
    # bulk_process_ppg_tables()

    # wavetable16_to_4KB_sample_source("8bit-RETRO_SP.WAV", "8bit-LIGHT_YE.WAV",
    #                            "8bit-SYNTH_VO.WAV", "voices-image.wav" )

    #wavetable16_to_1KB_sample_source("G:\\wavsyn\\wavetables\\1st_24", "1st_24.wav")
    #wavetable16_to_1KB_sample_source("G:\\wavsyn\\wavetables\\2nd_24", "2nd_24.wav")
    #wavetable16_to_1KB_sample_source("G:\\wavsyn\\wavetables\\3rd_24", "3rd_24.wav")
    #wavetable16_to_1KB_sample_source("G:\\wavsyn\\wavetables\\4th_24", "4th_24.wav")
    wavetable16_to_1KB_sample_source("G:\\wavsyn\\wavetables\\5th24", "5th_24.wav")
    exit(0)





    write_virus_directory_to_intermediate_wav("F:\\wavsyn\\wavetables\\virus", "virus_ti.wav" )
    exit(0)

    root_dir = "F:\\samples\\Fairlight CMI IIx Disks Image\\disks\\BIN\\IIx_disks\\New Voice Disks"
    source_folders = os.listdir(root_dir)
    print(source_folders)
    print(f'copying {len(source_folders)} folders of samples to multiple images')
    for child in source_folders:
        if child in ("Electric & Keyboard Inst. (6809) Series IIx", "Mode 1 (6809) Series IIx",
                     "Pianos (6809) Series IIx"):
            continue
        name = os.path.join(root_dir, child)
        write_fairlight_directory_to_intermediate_wav(name + "\\EXPORT\\VC2WAV", child.replace(' ', '_'))
