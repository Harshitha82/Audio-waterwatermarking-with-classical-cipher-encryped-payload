
import numpy as np
import os
import json

def calculate_snr(original_path, watermarked_path):
    # Load files
    from scipy.io import wavfile
    rate1, data1 = wavfile.read(original_path)
    rate2, data2 = wavfile.read(watermarked_path)
    
    if data1.shape != data2.shape:
        # Just in case length changed (shouldn't for LSB replacement)
        min_len = min(len(data1), len(data2))
        data1 = data1[:min_len]
        data2 = data2[:min_len]
        
    # Convert to float for calculation
    s = data1.astype(np.float64)
    n = (data1 - data2).astype(np.float64) # Noise is Difference
    
    # Power
    s_p = np.sum(s ** 2)
    n_p = np.sum(n ** 2)
    
    if n_p == 0:
        return float('inf') # Perfect copy
    
    snr = 10 * np.log10(s_p / n_p)
    return snr

class LearningModule:
    def __init__(self, history_file="learning_history.json"):
        self.history_file = history_file
        self.history = self._load()

    def _load(self):
        if not os.path.exists(self.history_file):
            return []
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except:
            return []
            
    def _save(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)

    def record_attempt(self, filename, size, bits_per_sample, success, snr=None):
        entry = {
            "filename": filename,
            "size": size,
            "bits": bits_per_sample,
            "success": success,
            "snr": snr
        }
        self.history.append(entry)
        self._save()

    def suggest_bits(self, size):
        # Simple heuristic based on history
        # Find similar size files that succeeded with high SNR
        # For now, just return a safe default if no history
        # If history exists, try to be aggressive if previous attempts worked.
        
        relevant = [h for h in self.history if abs(h['size'] - size) < 100000 and h['success']]
        
        if not relevant:
            return 1 # Conservative start
            
        # Check max bits that worked with good SNR (> 40dB)
        best_bits = 1
        for r in relevant:
            if r['snr'] and r['snr'] > 40 and r['bits'] > best_bits:
                best_bits = r['bits']
        
        return best_bits

if __name__ == "__main__":
    # Test
    # Assume 'test.wav' and 'out.wav' exist from stego test
    if os.path.exists("test.wav") and os.path.exists("out.wav"):
        snr = calculate_snr("test.wav", "out.wav")
        print(f"SNR: {snr:.2f} dB")
        
        lm = LearningModule()
        lm.record_attempt("test.wav", 1000, 2, True, snr)
        rec = lm.suggest_bits(1000)
        print(f"Recommended bits: {rec}")
