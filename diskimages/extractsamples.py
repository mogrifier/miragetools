# This will diskimages the data from a mirage disk image (original, not hfe)
# and write it out as 6 wavesample files. They are raw pcm data. Format is:
# mono, unsigned 8 bit, little-endian, 29411 Hz sample rate
# (depending on how sampled).
import sys
import os.path

def extract_wavesamples(filename):
    print("processing file " + filename)
    name_stub = os.path.basename(filename)
    # create six separate arrays of binary data, each initially 72704 bytes.
    # This contains the 64KB wavesample plus extra 512 byte sectors
    # and initial 1024 byte parameter data to be removed.
    mirage_disk = open(filename, 'rb')
    mirage_data = bytearray(mirage_disk.read())
    print(f'data read = {len(mirage_data)}.')

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
        print(f"***** processing {name} *****")
        wavesample = collapse_wave_data(data)
        write_wave_sample(wavesample, name)

# each block of data includes the wavesample data plus 512 byte chunks
# interspersed between mirage disk tracks. This will remove the extra
# data, returning just the wavesample data (64KB).


def collapse_wave_data(samples):
    clean_wavesample = bytearray(66560)
    wave_data = 5120
    skip_data = 512
    track_length = 5632

    for start in range(13):
        end = start * wave_data + wave_data
        print(f"copying bytes {start * track_length}:{start * track_length + wave_data}")
        print(f"to {start * wave_data}:{end}")
        clean_wavesample[start * wave_data:end] = \
            samples[start * track_length:start * track_length + wave_data]

    # skip first 1024 bytes of parameter data
    return clean_wavesample[1024:66560]

# Write a 64KB wave file. File is mono, 8bit unsigned PCM. Sample rate is unknown, but
# default is 29411Hz, so the sample is about 2 seconds long. To get the actual sample rate,
# you need to know how to read the parameter data from the disk and what it means.


def write_wave_sample(samples, name):
    output = open(name, 'wb')
    output.write(samples)


if __name__ == '__main__':
    # read and pass file name argument
    if len(sys.argv) != 2:
        print("A file name and absolute path is required. Exiting.")
        sys.exit(1)
    else:
        extract_wavesamples(sys.argv[1])

