import os
import numpy as np
import struct
import soundfile as sf
import matplotlib.pyplot as plt
from math import gcd
from scipy.signal import resample_poly

def resample_waveform(data, new_length):
    original_length = len(data)
    
    factor = gcd(original_length, new_length)
    
    up = new_length // factor
    down = original_length // factor
    
    return resample_poly(data, up, down)

def reverse_byte(byte_val):
    if byte_val < 0:  # if the byte represents a negative number
        byte_val = 256 + byte_val  # convert to its 2's complement positive equivalent
    return int('{:08b}'.format(byte_val & 0xFF)[::-1], 2)

def apply_ramp(data, ramp_length=10):
    # If the waveform is shorter than twice the ramp length, adjust the ramp length
    if len(data) < 2 * ramp_length:
        ramp_length = len(data) // 2

    # Create the ramp
    ramp = np.linspace(0, 1, ramp_length)

    # Apply fade-in and fade-out
    data[:ramp_length] *= ramp
    data[-ramp_length:] *= ramp[::-1]

    return data

def plot_waveforms(original, downsampled):
    plt.figure(figsize=(10, 5))
    
    # Plot original waveform
    plt.plot(original, label="Original", alpha=0.7)
    
    # Plot downsampled waveform, stretched to match the length of the original
    x_new = np.linspace(0, len(original) - 1, len(downsampled))
    plt.plot(x_new, downsampled, label="Downsampled", linestyle='dashed', alpha=0.7)
    
    plt.title("Waveform Comparison")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def process_filename(filename):
    # Extract the first 6 characters of the filename
    name = filename[:6]
    
    # Prepend with 2 spaces
    name = "  " + name
    
    # Apply bit reversal on each character
    reversed_bytes = bytes([reverse_byte(ord(char)) for char in name])
    
    return reversed_bytes


def process_files_in_directory(directory):
    # List all .wav files in the directory
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith('.wav')]
    files.sort()
    
    if len(files) > 128:
        raise ValueError("Too many files in the directory. Maximum allowed is 128.")
    
    output_filename = os.path.join(directory, "output.shapewt")
    name_output_filename = os.path.join(directory, "names_output.bin")
    
    # Process each file and append to the output file
    with open(output_filename, 'wb') as output_file:
        for filename in files:
            #with wave.open(os.path.join(directory, filename), 'rb') as serum_wt:
            data, samplerate = sf.read(os.path.join(directory, filename))
            #samples = (data * 32767).astype(np.int16).tolist()
            samples = data.tolist()

            num_waveforms = len(samples) // 2048


            indices_to_take = [0]  # Always take the first waveform

            if num_waveforms > 8:
                # Calculate the intervals for selecting the next 6 waveforms
                interval = (num_waveforms - 1) / 7
                for i in range(1, 7):
                    indices_to_take.append(int(round(i * interval)))

                indices_to_take.append(num_waveforms - 1)  # Always take the last waveform
            elif num_waveforms == 8:
                indices_to_take.extend(range(1, 7))
            else:
                indices_to_take.extend(range(1, num_waveforms))
                # add the last waveform 8-n times to the end if there are less than 8 waveforms
                indices_to_take.extend([num_waveforms - 1] * (8 - num_waveforms))
                
            assert len(indices_to_take) == 8, "Invalid number of waveforms to take."

            print(f"Processing file {filename} with {num_waveforms} waveforms. Taking waveforms {indices_to_take}.")
            
            # Check if the wavetable has the expected number of samples
            if len(samples) % 2048 != 0:
                raise ValueError(f"Invalid Serum wavetable format in file {filename}.")
            
            # Extract the selected waveforms
            converted_samples = []
            for idx in indices_to_take:
            #for i in range(0, len(samples), 32 * 2048):  # Take every 32nd cycle
                #cycle_samples = samples[i:i+2048]
                cycle_samples = samples[idx*2048: (idx+1)*2048]
                
                # Downsample using sinc interpolation
                #downsampled_cycle = sinc_interpolation(cycle_samples, 512)
                downsampled_cycle = resample_waveform(cycle_samples, 512)

                downsampled_cycle = apply_ramp(downsampled_cycle, 10)
                #plot_waveforms(cycle_samples, downsampled_cycle)

                downsampled_cycle = (downsampled_cycle * 32767).astype(np.int16).tolist()
                converted_samples.extend(downsampled_cycle)
            
            # Reverse the bits in each byte
            for sample in converted_samples:
                lo_byte = reverse_byte(sample & 0xFF)  # Lower 8 bits
                hi_byte = reverse_byte((sample >> 8) & 0xFF)  # Higher 8 bits
                output_file.write(struct.pack('<BB', lo_byte, hi_byte))

            with open(name_output_filename, 'ab') as name_file:
                name_file.write(process_filename(filename))




import sys
# get the path from the command line
target_path = sys.argv[1]

process_files_in_directory(target_path)

print('done')