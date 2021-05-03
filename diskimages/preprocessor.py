# Preprocessing functions on raw PCM files to ensure they are in format
# expected by writediskimage.py. The format is a single PCM file containing
# 6 * 64KB chunks of 8bit, mono, pcm data. The routines in this file are highly
# specific. Add your own!
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


if __name__ == '__main__':
    wavetable16_to_sample_source("8bit-RRLYRQ5.WAV", "8bit-RRLYRQ6.WAV",
                                 "8bit-RRLYRQ7.WAV", "rrlyrq-image.wav" )