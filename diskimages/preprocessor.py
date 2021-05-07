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
        #write each table twice (lower and upper half)
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
    bulk_process_ppg_tables()


    #wavetable16_to_4KB_sample_source("8bit-RETRO_SP.WAV", "8bit-LIGHT_YE.WAV",
    #                            "8bit-SYNTH_VO.WAV", "voices-image.wav" )