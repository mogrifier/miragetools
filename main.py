# This will extract the data from a mirage disk image (original, not hfe)
# and write it out as 6 wavesample files. They are raw pcm data. Format is:
# mono, unsigned 8 bit, little-endian, 32000 Hz sample rate.
import sys
import os.path

def extract_wavesamples(filename):
    print("processing file " + filename)
    name_stub = os.path.basename(filename)
    # create six separate arrays of binary data, each initially 72704 bytes.
    # This contains the 64kb wavesample plus extra 512 byte sectors
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
    sample_metadata = {name_stub + "_lh1.wav": 2, name_stub + "_lh2.wav": 15,
                       name_stub + "_lh3.wav": 28, name_stub + "_uh1.wav": 41,
                       name_stub + "_uh2.wav": 54, name_stub + "_uh3.wav": 67}

    for name, track in sample_metadata.items():
        # create a new byte array containing correct data (64kb chunk)
        offset = track * track_length
        data = bytearray(mirage_data[offset:offset + sample_size])
        wavesample = remove_short_sectors(data)
        write_wave_sample(wavesample, name)

# each block of data includes the wavesample data plus 512 byte chunks
# interspersed between mirage disk tracks. This will remove the extra
# data, returning just the wavesample data (64kb).


def remove_short_sectors(samples):
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

# Write a 64kb wave file. File is mono, 8bit unsigned PCM at 32KHz. Create
# a proper wav header for easy import into audio software. Or be lazy and
# give raw.


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

