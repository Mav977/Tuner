# 🎵 Tuner

**Tuner** is a robust audio fingerprinting and recognition engine built with Python. It listens to audio snippets — via microphone or file upload — and identifies songs in real-time by matching them against a high-speed spectral database.

Think of it as your own open-source version of Shazam, running locally with a Streamlit interface.

---

## ✨ Key Features

- **Band-Aware Peak Extraction** — Splits the spectrogram into fixed frequency bands and keeps only the strongest peaks per frame.
- **Adaptive Noise Filtering** — Uses median-based thresholds to ignore weak or noisy frequency components.
- **Compact Bit-Packed Hashing** — Encodes `(f1, f2, Δt)` relationships between peak pairs into a single integer hash for fast lookup.
- **Temporal Voting Matcher** — Identifies tracks by clustering consistent time offsets between matching fingerprints.
- **Lightweight Audio Processing** — Runs at 11 kHz mono with a small STFT, keeping computation fast and efficient.
---

## 🛠️ Installation

### 1. Prerequisites

You need **Python 3.8+** and **FFmpeg** installed on your system.

**Windows:** Download FFmpeg and add it to PATH
**Mac:**

```bash
brew install ffmpeg
```

**Linux:**

```bash
sudo apt install ffmpeg
```

---

### 2. Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/Mav977/Tuner.git
cd Tuner
pip install -r requirements.txt
```

#### Required Python Packages

* streamlit (UI)
* librosa (Audio processing)
* numpy (Math & Signal processing)
* pydub (Audio format conversion)
* yt-dlp (YouTube downloading)
* matplotlib (Visualization)

---

## 🚀 How to Run

Launch the web interface:

```bash
streamlit run app.py
```

---

## Usage Workflow

### Build Database (Left Sidebar)

* Paste a YouTube URL to download and index a track
* Or drag-and-drop local audio files to add them to the system

### Identify Audio (Main Tab)

* Click **Record Snippet** to use your microphone
* Or upload a short clip (e.g., 12-20 seconds)

### Analyze Results

* View the match confidence score
* Expand **View Recording Peaks** to compare the visual fingerprint of your recording against the database

---

## 🧠 How It Works (Simplified)


**Spectrogram:**
The audio is turned into a picture that shows which frequencies play over time.

**Peak Map:**
Background noise is reduced, and only the strongest sound points are kept.

**Hashing:**
These strong points are linked together and converted into compact numeric fingerprints.

**Matching:**
When new audio is recorded, its fingerprints are compared with the database. If many fingerprints line up at the same time position, the song is identified.


---

## ⚙️ Configuration

You can tune the algorithm’s sensitivity in `backbone.py`.

| Variable   | Default | Effect                                                                        |
| ---------- | ------- | ----------------------------------------------------------------------------- |
| PEAK_DELTA | 15      | How much louder a peak must be than the background. Increase for noisy rooms. |
| MIN_AMP    | -60     | Silence threshold (dB). Decrease to -70 for very quiet recordings.            |
| MAX_PEAKS  | 5       | Maximum fingerprint points kept per time frame.                               |

---

## 📂 Project Structure

```
app.py             # Streamlit frontend and state management
backbone.py        # Core engine (fingerprinting, hashing, matching)
yt.py              # yt-dlp wrapper for downloads
```
