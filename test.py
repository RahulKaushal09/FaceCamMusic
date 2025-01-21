import os
import cv2
import time
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import yt_dlp
from pyaudio import PyAudio, paInt16
from pycaw.pycaw import AudioUtilities
from pycaw.api.endpointvolume import IAudioEndpointVolume
from comtypes import CLSCTX_ALL

# Load environment variables
load_dotenv()

# Spotify credentials
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
SPOTIFY_SCOPE = "user-read-playback-state user-modify-playback-state"

# Initialize Spotify client
sp = Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SPOTIFY_SCOPE
))

# Function to play audio stream
def play_audio_stream(url):
    chunk = 1024
    pa = PyAudio()
    stream = pa.open(format=paInt16, channels=2, rate=44100, output=True)

    # Download and play the audio stream
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info["url"]
        print(f"Playing from URL: {audio_url}")
        data = ydl.urlopen(audio_url).read(chunk)
        while data:
            stream.write(data)
            data = ydl.urlopen(audio_url).read(chunk)

    stream.stop_stream()
    stream.close()
    pa.terminate()

# Control system audio volume
def set_audio_volume(mute: bool):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)
    volume.SetMute(mute, None)
    print("Muted" if mute else "Unmuted")

# Face detection using OpenCV
def is_face_detected():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(0)  # Access the webcam
    ret, frame = cap.read()
    if not ret:
        print("Webcam not accessible.")
        return False

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    cap.release()
    return len(faces) > 0

# Main function
def main():
    # Search for a track on Spotify
    query = "Shape of You"  # Replace with your desired song
    results = sp.search(q=query, type="track", limit=1)
    if not results["tracks"]["items"]:
        print("No tracks found.")
        return

    track = results["tracks"]["items"][0]
    print(f"Playing: {track['name']} by {track['artists'][0]['name']}")

    # Stream and play audio
    youtube_url = f"https://www.youtube.com/results?search_query={track['name']} {track['artists'][0]['name']}"
    print(f"Fetching audio stream from: {youtube_url}")
    play_audio_stream(youtube_url)

    # Continuously check for face detection
    while True:
        if is_face_detected():
            set_audio_volume(False)  # Unmute
        else:
            set_audio_volume(True)  # Mute
        time.sleep(5)

if __name__ == "__main__":
    main()
