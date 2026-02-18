import os
import yt_dlp
from backbone import load_audio, compute_spec, extract_peaks, generate_fingerprint, find_match

def download_audio_from_yt(url, output_path="downloads"):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        'postprocessor_args': ['-ar', '11000', '-ac', '1'], # Downsample during download
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    return [os.path.join(output_path, f) for f in os.listdir(output_path) if f.endswith('.wav')]

def build_database(playlist_url):
    print("--- Downloading Playlist ---")
    files = download_audio_from_yt(playlist_url)
    
    master_db = {}
    for i, file_path in enumerate(files):
        print(f"Indexing: {os.path.basename(file_path)}")
        y, sr = load_audio(file_path)
        spec = compute_spec(y)
        peaks = extract_peaks(spec)
        master_db = generate_fingerprint(peaks, file_path, db=master_db)
    
    return master_db

if __name__ == "__main__":

    url = input("Enter YouTube Playlist/Video URL: ")
    db = build_database(url)
    print(f"Database built with {len(db)} unique hashes.")
    
   