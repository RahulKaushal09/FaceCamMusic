import cv2
import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import time

# Load environment variables from .env file
load_dotenv()

# Spotify credentials from .env
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

# Initialize Spotify API
sp = Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="user-read-playback-state user-modify-playback-state"))

devices = sp.devices()  # Get available devices
print("Available devices:", devices)

# Use a specific device ID from the devices list
device_id = devices['devices'][0]['id'] 
# Initialize OpenCV face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Function to mute/unmute system audio
def set_volume(mute):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)
    if mute:
        volume.SetMute(1, None)  # Mute
    else:
        volume.SetMute(0, None)  # Unmute

# Function to play music
def play_music():
    sp.start_playback()
    print("Playing music...")

# Function to pause music
def stop_music():
    sp.pause_playback()
    print("Music paused")

# Open the camera
cap = cv2.VideoCapture(0)

# Start playing music
play_music()

# Variable to track mute state
muted = False

try:
    while True:
        # Capture video frame
        ret, frame = cap.read()
        # if not ret:
        #     break

        # Convert frame to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:  # No face detected
            if not muted:
                set_volume(True)
                muted = True
                stop_music()
        else:  # Face detected
            if muted:
                set_volume(False)
                muted = False
                play_music()

        # Display the video feed with detected faces (for debugging)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        cv2.imshow('Face Detection', frame)

        # Exit loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Release the camera and close OpenCV windows
    cap.release()
    cv2.destroyAllWindows()
    stop_music()
