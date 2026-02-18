import streamlit as st
from streamlit_mic_recorder import mic_recorder
import io
import os
import librosa
import numpy as np
from pydub import AudioSegment

# Import from our custom modules
from backbone import compute_spec, extract_peaks, generate_fingerprint, find_match, load_audio, plot_constellation, SR
from yt import download_audio_from_yt

st.set_page_config(page_title="Audio Recognizer", page_icon="🎵", layout="wide")
st.title("🎵 Universal Audio Fingerprinter")

# --- SESSION STATE INITIALIZATION ---
if 'master_db' not in st.session_state:
    st.session_state.master_db = {}
if 'indexed_songs' not in st.session_state:
    st.session_state.indexed_songs = []
if 'db_peaks' not in st.session_state:
    st.session_state.db_peaks = {} # Stores peaks permanently for plotting

# --- SIDEBAR: DATABASE BUILDING ---
with st.sidebar:
    st.header("1. Build Database")
    
    # Option A: YouTube
    playlist_url = st.text_input("YouTube URL (Video or Playlist)")
    if st.button("Download & Index YT") and playlist_url:
        with st.spinner("Downloading and processing YT..."):
            files = download_audio_from_yt(playlist_url)
            for file_path in files:
                song_name = f"YT: {os.path.basename(file_path)}"
                if song_name not in st.session_state.indexed_songs:
                    y, sr = load_audio(file_path)
                    peaks = extract_peaks(compute_spec(y))
                    
                    st.session_state.db_peaks[song_name] = peaks # Save peaks to memory
                    st.session_state.master_db = generate_fingerprint(peaks, song_name, db=st.session_state.master_db)
                    st.session_state.indexed_songs.append(song_name)
            st.success("YouTube files indexed!")

    st.divider()
    
    # Option B: Local Upload
    uploaded_files = st.file_uploader("Upload local songs", type=['wav', 'mp3', 'm4a'], accept_multiple_files=True)
    if st.button("Index Local Files") and uploaded_files:
        with st.spinner("Processing local files..."):
            for uploaded_file in uploaded_files:
                song_name = f"Local: {uploaded_file.name}"
                if song_name not in st.session_state.indexed_songs:
                    y, _ = librosa.load(uploaded_file, sr=SR, mono=True)
                    peaks = extract_peaks(compute_spec(y))
                    
                    st.session_state.db_peaks[song_name] = peaks # Save peaks to memory
                    st.session_state.master_db = generate_fingerprint(peaks, song_name, db=st.session_state.master_db)
                    st.session_state.indexed_songs.append(song_name)
            st.success("Local files indexed!")

    # Display Persistent Plots
    st.divider()
    st.write(f"### Indexed Library ({len(st.session_state.indexed_songs)})")
    for song in st.session_state.indexed_songs:
        st.caption(f"✅ {song}")
        if song in st.session_state.db_peaks:
            with st.expander(f"📊 View Peaks: {song[:20]}..."):
                fig_db = plot_constellation(st.session_state.db_peaks[song], title=song)
                st.pyplot(fig_db)

# --- MAIN AREA: IDENTIFICATION ---
st.header("2. Identify Audio")
tab1, tab2 = st.tabs(["🎙️ Record Snippet", "📁 Upload Query File"])

y_query = None

with tab1:
    audio_record = mic_recorder(start_prompt="Start Recording", stop_prompt="Stop & Process", key='recorder')
    if audio_record:
        # Safely convert browser audio to a format Librosa can read
        audio_bytes = io.BytesIO(audio_record['bytes'])
        audio = AudioSegment.from_file(audio_bytes)
        wav_buffer = io.BytesIO()
        audio.export(wav_buffer, format="wav")
        wav_buffer.seek(0)
        y_query, _ = librosa.load(wav_buffer, sr=SR, mono=True)

with tab2:
    query_file = st.file_uploader("Upload snippet to identify", type=['wav', 'mp3', 'm4a'], key="query_upload")
    if query_file:
        y_query, _ = librosa.load(query_file, sr=SR, mono=True)

# --- MATCHING ENGINE ---
if y_query is not None:
    y_query = y_query.astype(np.float32)
    with st.spinner("Analyzing and Searching..."):
        peaks_rec = extract_peaks(compute_spec(y_query))
        
        # Plot the Query Peaks
        with st.expander("📊 View Recording Peaks", expanded=True):
            fig_rec = plot_constellation(peaks_rec, title="Recorded Audio Peaks")
            st.pyplot(fig_rec)

        fingerprints_rec = generate_fingerprint(peaks_rec, "QUERY")
        matches = find_match(st.session_state.master_db, fingerprints_rec)

    if matches:
        st.balloons()
        st.subheader("Match Found! 🏆")
        for song_id, score in matches[:3]:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{song_id}**")
                st.progress(min(score / 150, 1.0)) # Visual bar
            with col2:
                st.write(f"Score: {score}")
            st.divider()
    else:
        st.error("No match found. Ensure the song is indexed and check the peak plot to ensure your mic isn't capturing only silence/noise.")

if y_query is not None:
    with st.expander("🔊 Listen to captured audio"):
        st.audio(y_query, sample_rate=SR)