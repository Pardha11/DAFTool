import json
import pyaudio
import numpy as np

delay_time = 0
with open('config.json') as f:
    data = json.load(f)
    delay_time = data['delay']

mod_freq = 0.2
mod_depth = 0.005
mix = 0.5

p = pyaudio.PyAudio()

input_stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

output_stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True)

delay_samples = int(delay_time * 44100)
delay_buffer = np.zeros(delay_samples, dtype=np.float32)
buffer_pos = 0

lfo = np.sin(2*np.pi*mod_freq*np.arange(44100)/44100).astype(np.float32)

while True:
    input_block = input_stream.read(1024)
    
   
    input_data = np.frombuffer(input_block, dtype=np.int16).astype(np.float32) / 32768.0
    
    # Apply the chorus effect to the input block
    output_data = np.zeros_like(input_data)
    for n in range(len(input_data)):
        # Add the input sample to the delay line buffer
        delay_buffer[buffer_pos] = input_data[n]
        
        # Compute the modulated delay line index
        mod_idx = buffer_pos + int(mod_depth * delay_samples * lfo[n])
        
        # Read the delayed sample from the buffer
        delayed_sample = delay_buffer[mod_idx % delay_samples]
        
        # Mix the original and delayed sample
        output_data[n] = (1-mix) * input_data[n] + mix * delayed_sample
        
        # Update the delay line buffer position
        buffer_pos += 1
        buffer_pos %= delay_samples
    
   
    output_block = (output_data * 32768.0).astype(np.int16).tobytes()
    
    
    output_stream.write(output_block)
