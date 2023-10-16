import sys
import os
from crccheck.crc import Crc16IbmSdlc

WAVE_SIZE = 512 * 2 * 8  # Size of a single wave in bytes
MAX_WAVES = 127          # Maximum number of waves
START_OFFSET = 0x10009B  # Starting offset in bytes
NAME_OFFSET = 0xF009B

def main(target_file, wavebank_file, start_index):
    # Ensure start index is within bounds
    if start_index < 0 or start_index >= MAX_WAVES:
        print("Error: Start index out of bounds.")
        return

    # Calculate size of wavebank file to determine number of waves it contains
    wavebank_size = os.path.getsize(wavebank_file)
    num_waves_in_bank = wavebank_size // WAVE_SIZE

    # Check the name bank file size and number of names
    namebank_file = wavebank_file.replace("output.shapewt", "names_output.bin")
    namebank_size = os.path.getsize(namebank_file)
    num_names_in_bank = namebank_size // 8

    if num_names_in_bank != num_waves_in_bank:
        print("Error: Mismatch between number of names and number of waves.")
        return


    print('wavebank_size', wavebank_size)
    print('num_waves_in_bank', num_waves_in_bank)

    # Ensure the wavebank file is a valid size
    if wavebank_size % WAVE_SIZE != 0:
        print("Error: Invalid wavebank file size.")
        return

    # Ensure we don't exceed the 128 wave limit
    if start_index + num_waves_in_bank > MAX_WAVES:
        print(f"Error: Wavebank exceeds maximum limit with the given start index, {start_index}, and contains {num_waves_in_bank} waves, total of {start_index + num_waves_in_bank}.")
        return

    # Overwrite the target file with wavebank data at the specified offset
    with open(target_file, 'r+b') as target, open(wavebank_file, 'rb') as bank:
        target.seek(START_OFFSET + start_index * WAVE_SIZE)
        target.write(bank.read())

    # Write the name data to the target file at the specified offset
    with open(target_file, 'r+b') as target, open(namebank_file, 'rb') as namebank:
        target.seek(NAME_OFFSET + start_index * 8)
        target.write(namebank.read())

    print(f"Successfully wrote {num_waves_in_bank} waves to {target_file} starting at index {start_index}.")
    # print memory location of the start of the wavebank
    print(f"Start of new wavebank: {hex(START_OFFSET + start_index * WAVE_SIZE)}")
    # print memory location of the end of the wavebank
    print(f"End of new wavebank: {hex(START_OFFSET + start_index * WAVE_SIZE + num_waves_in_bank * WAVE_SIZE)}")

    # print locations of names too
    print(f"Start of new names: {hex(NAME_OFFSET + start_index * 8)}")
    print(f"End of new names: {hex(NAME_OFFSET + start_index * 8 + num_names_in_bank * 8)}")

    # Remove the last 2 bytes (old checksum)
    with open(target_file, 'r+b') as target:
        target.seek(-2, os.SEEK_END)
        target.truncate()

    # Compute the CRC for the file without the last 2 bytes
    with open(target_file, 'rb') as target:
        file_data = target.read()
        crc_value = Crc16IbmSdlc.calc(file_data)

    # Append the computed CRC to the end of the file
    with open(target_file, 'a+b') as target:
        target.write(crc_value.to_bytes(2, 'little'))

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: script.py <target_file> <wavebank_file> <start_index>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], int(sys.argv[3]))
