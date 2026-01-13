import numpy as np
from scipy.io import wavfile

def text_to_bits(text):
    bits = bin(int.from_bytes(text.encode('utf-8'), 'big'))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))

def bits_to_text(bits):
    n = int(bits, 2)
    return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode('utf-8', errors='ignore')

def embed_message(input_path, output_path, message, bits_per_sample=1):
    rate, data = wavfile.read(input_path)
    
    # Ensure data is integer type
    if data.dtype == np.float32:
        # Convert to int16 if float
        data = (data * 32767).astype(np.int16)
    
    # Flatten checks
    orig_shape = data.shape
    flat_data = data.flatten()
    
    # Prepare message
    # We need to embed length first or use a delimiter. 
    # For simplicity, let's embed 32-bit length prefix.
    msg_bits = text_to_bits(message)
    length_bin = bin(len(msg_bits))[2:].zfill(32) 
    full_bits = length_bin + msg_bits
    
    total_slots = len(flat_data) * bits_per_sample
    if len(full_bits) > total_slots:
        raise ValueError(f"Message too long for audio file. Need {len(full_bits)} bits, have {total_slots}.")
    
    # Embedding
    bit_idx = 0
    # Create mask
    # e.g. bits_per_sample=2 -> mask 0b11 -> 3. Inverse is ~3.
    mask = (1 << bits_per_sample) - 1
    
    # Vectorized approach or iterative?
    # Iterative is safer for variable length not matching array size exactly.
    # But slow in Python.
    # However, for a demo, iterative might be too slow for large files.
    # Let's try to do it somewhat efficiently.
    
    # We modify the flat_data in place
    # We only modify the first N samples needed
    samples_needed = (len(full_bits) + bits_per_sample - 1) // bits_per_sample
    print("bitssss",samples_needed)
    for i in range(samples_needed):
        sample = flat_data[i]
        
        # Get bits for this sample
        chunk = full_bits[bit_idx : bit_idx + bits_per_sample]
        bit_idx += bits_per_sample
        
        # Pad chunk if last one
        if len(chunk) < bits_per_sample:
            chunk = chunk.ljust(bits_per_sample, '0')
            
        val = int(chunk, 2)
        
        # Clear LSBs
        sample = sample & ~mask
        # Set LSBs
        sample = sample | val
        
        flat_data[i] = sample
        
    reshaped_data = flat_data.reshape(orig_shape)
    wavfile.write(output_path, rate, reshaped_data)
    return len(full_bits)

def extract_message(input_path, bits_per_sample=1):
    rate, data = wavfile.read(input_path)
    if data.dtype == np.float32:
         data = (data * 32767).astype(np.int16)
         
    flat_data = data.flatten()
    
    mask = (1 << bits_per_sample) - 1
    
    # Extract first 32 bits for length
    # How many samples?
    length_bits = ""
    idx = 0
    
    # Extract length
    # We need 32 bits. 
    # samples_for_len = ceil(32 / bits)
    samples_for_len = (32 + bits_per_sample - 1) // bits_per_sample
    
    for i in range(samples_for_len):
        sample = flat_data[i]
        val = sample & mask
        chunk = bin(val)[2:].zfill(bits_per_sample)
        length_bits += chunk
        
    # Truncate to exactly 32
    length_val_str = length_bits[:32]
    msg_len = int(length_val_str, 2)
    
    # Now extract message
    # Start from where we left off? 
    # Actually, simpler logic: extract all bits needed.
    
    total_bits_needed = 32 + msg_len
    total_samples_needed = (total_bits_needed + bits_per_sample - 1) // bits_per_sample
    
    extracted_bits = ""
    # We can optimize this by just reading the array
    # But let's reuse the loop for clarity or just continue
    # Ideally reuse
    
    # Let's restart to be clean
    # or just continue from `samples_for_len`?
    # The `length_bits` might have had extra bits if 32 wasn't divisible by `bits_per_sample`.
    # To handle this correctly, we should just stream bits.
    
    extracted_stream = ""
    for i in range(total_samples_needed):
        sample = flat_data[i]
        val = sample & mask
        chunk = bin(val)[2:].zfill(bits_per_sample)
        extracted_stream += chunk
        
    # Cut
    final_bits = extracted_stream[32 : 32 + msg_len]
    return bits_to_text(final_bits)

if __name__ == "__main__":
    # Test
    # Create dummy wav
    rate = 44100
    t = np.linspace(0, 1, rate)
    data = (np.sin(2*np.pi*440*t) * 32767).astype(np.int16)
    wavfile.write("test.wav", rate, data)
    
    msg = "SecretMessage123"
    print(f"Embedding: {msg}")
    embed_message("test.wav", "out.wav", msg, bits_per_sample=2)
    
    recovered = extract_message("out.wav", bits_per_sample=2)
    print(f"Recovered: {recovered}")
