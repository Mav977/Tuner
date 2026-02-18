import numpy as np
import librosa
import matplotlib.pyplot as plt

# --- CONSTANTS ---
N_FFT = 1024
HOP_LENGTH = 512
SR = 11000

BANDS = [
    (0, 10), (10, 20), (20, 40), (40, 80), (80, 120), 
    (120, 160), (160, 210), (210, 270), (270, 340), 
    (340, 420), (420, 512)
]

def load_audio(file):
    y, sr = librosa.load(file, sr=SR, mono=True)
    return y, sr

def compute_spec(y, n_fft=N_FFT, hop_length=HOP_LENGTH):
    # Librosa applies a Hann window automatically here!
    stft = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    return np.abs(stft)

def extract_peaks(spectrogram, sr=SR, n_fft=N_FFT, hop_length=HOP_LENGTH):
    freq_bins, time_frames = spectrogram.shape
    freq_resolution = sr / n_fft
    spectrogram_db = librosa.amplitude_to_db(spectrogram, ref=np.max)
    
    MIN_AMP = -60
    PEAK_DELTA = 15 
    MAX_PEAKS_PER_FRAME = 10 # Prevent noise from overcrowding the map
    peaks = []

    for t in range(time_frames):
        frame_db = spectrogram_db[:, t]
        candidates = []
        
        for band_min, band_max in BANDS:
            band = frame_db[band_min:band_max]
            if len(band) == 0: continue
            
            max_idx = np.argmax(band)
            candidates.append((band[max_idx], band_min + max_idx))

        if not candidates: continue
        
        
        band_median = np.median([c[0] for c in candidates]) 
        
        candidates.sort(key=lambda x: x[0], reverse=True)
        
        count = 0
        for mag, f_bin in candidates:
            if count >= MAX_PEAKS_PER_FRAME: break
            
            if mag > PEAK_DELTA + band_median and mag > MIN_AMP:
                time_sec = t * hop_length / sr
                freq_hz = int(f_bin * freq_resolution)
                peaks.append((time_sec, freq_hz))
                count += 1
                
    return np.array(peaks, dtype=np.float32)

def create_address(anchor, zonepoint):
    t1, f1 = anchor
    t2, f2 = zonepoint
    
   
    f1_idx = int(f1) & 8191  # 13 bits
    f2_idx = int(f2) & 8191  # 13 bits
    delta_ms = int((t2 - t1) * 1000) & 32767 # 15 bits
    
    # Shift F1 by 28 (15 + 13) to make room for F2 and Delta
    return (f1_idx << 28) | (f2_idx << 15) | delta_ms

def generate_fingerprint(peaks, song_id, db=None):
    if db is None: db = {}
    targetsize = 15 
    
    for i in range(len(peaks)):
        anchor = peaks[i]
        for j in range(i + 3, min(i + 3 + targetsize, len(peaks))):
            address = create_address(anchor, peaks[j])
            if address not in db: db[address] = []
            db[address].append({"anchor_time_ms": int(anchor[0] * 1000), "song_id": song_id})
    return db

def find_match(db_fingerprint, recorded_fingerprint):
    match_votes = {}
    common_hashes = set(recorded_fingerprint.keys()) & set(db_fingerprint.keys())

    for address in common_hashes:
        for rec_item in recorded_fingerprint[address]:
            for db_item in db_fingerprint[address]:
                offset_bucket = (db_item["anchor_time_ms"] - rec_item["anchor_time_ms"]) // 100
                vote_key = (db_item["song_id"], offset_bucket)
                match_votes[vote_key] = match_votes.get(vote_key, 0) + 1

    if not match_votes: return None
    
    song_scores = {}
    for (song_id, _), count in match_votes.items():
        song_scores[song_id] = max(song_scores.get(song_id, 0), count)
    
    return sorted(song_scores.items(), key=lambda x: x[1], reverse=True)

def plot_constellation(peaks, title="Constellation Map"):
    fig, ax = plt.subplots(figsize=(10, 3))
    if len(peaks) > 0:
        ax.scatter(peaks[:, 0], peaks[:, 1], s=3, c='red', marker='o')
    ax.set_title(title)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency (Hz)")
    ax.set_ylim(0, 5500)
    plt.tight_layout()
    return fig