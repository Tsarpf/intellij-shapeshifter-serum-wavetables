# Use at your own risk!!! 
You may for example:
- Destroy your PC OS by accidentally writing random binary stuff to the middle of a critical file on your computer
- Destroy your Shapeshifter by writing something where you shouldn't have and running that firmware
- I will take absolutely zero responsibility if you use this tool to brick or break your expensive eurorack module.

Only tested with the 2.0.4 jic, and the offsets are calculated for that version only. Previous (or future?) firmware versions will not work, but if you understand what the scripts are doing it's easy to change and apply this to other versions.

# What it is
Two scripts, one converts a folder containing serum format wavetables/WAVs to a binary blob (along with first 6 characters of their filename)
The writer also handles fixing the `.jic` file checksum so it works with Quartus (first time I've heard anyone solve this!). So no need to use the super slow Terasic writer with the raw EPCS dump

The offsets in the binary file seem to sometimes change between firmware versions, so be sure to set the offsets to match your firmware version binary format.

# What it does exactly
- Downsamples Serum format wavetables (.wavs) from 2048 to 512 samples using `resample_poly` from scipy's signal processing library
- Since a Serum wavetable can have anything between 1 and 512 waveforms, and Shapeshifter only supports 8, it takes the first and last waveform, and takes 6 evenly spread out waveforms between them to form the 8 waveforms (specific waveforms from the table are chosen, no interpolation is done in this step).
  - If there are less than 8 waveforms in the Serum wavetable, it just takes all of them, and repeats the last one until all 8 are filled
- To avoid crackles, the beginning and end of each waveform has a 10 sample linear ramp so that the waveforms start and end at exactly 0
- The `wavewriter.py` overwrites parts of the firmware `.jic` file at specific memory locations, **AND** reapplies the CRC checksum to the firmware file so that Quartus Programmer will accept it.
  - The checksum is CRC-16-IBM-SLDC, found out through 12 hours of digging into the Cyclone IV manuals and comparing changes between Shapeshifter firmware binaries to locate the checksum, and finally applying CRC RevEng when it was clear it was a CRC


# How to use
- Make sure you have downloaded the 2.0.4 firmware file to begin with. This will not work for other files
- `pip install matplotlib scipy numpy soundfile crccheck` to install deps (you can remove matplotlib if you don't want to look at the downsampling results visually, then also remove the import for that library)
- `python3 serum_to_shapeshifter.py ./PATH/TO/FOLDER/WITH/WAVS/IN/SERUM/FORMAT`
  - This will create two files `output.shapewt`, and `names_output.bin` in the same directory as the wav files
- `python3 wavewriter.py your_firmware_file.2.0.4.jic path/to/output.shapewt STARTING_INDEX` replace `STARTING_INDEX` by a value between 0-126 (127 index ie. 128th wave is used for controlling wave selection with Mod B input) where you want to place the waveforms in your Shapeshifter memory.
  - Given eg. 50 as the STARTING_INDEX and targeting the Serum "Spectral" wavetable folder with 35 tables (`.wav`s), the indices 50-85 would be filled with those waveforms.
  - Make absolutely sure you don't target some other file instead of the firmware file, as the script will just overwrite the specified part of the file without any checks whether it's actually the firmware file. So this step is _DANGEROUS_.
- After using `wavewriter.py` you now go through your firmware file with a binary diff tool to compare it to the original firmware, and check that you didn't touch addresses outside the wave name and wave data areas. Accidentally writing somewhere else could cause your Shapeshifter to malfunction.
- Follow the manual to flash your new `something.jic` into the device.
