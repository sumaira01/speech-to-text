from flask import Flask, render_template, request, jsonify
import random
import sounddevice as sd
import numpy as np
import wave
import requests
import time

app = Flask(__name__)

GLADIA_API_URL = "https://api.gladia.io/audio/text/audio-transcription/"
# API_KEY = "3183cfd2-289d-4900-a226-05e5fe5fc2ee"
API_KEY = "3183cfd2-289d-4900-a226-05e5fe5fc2ee"

FRUITS = {
    "en": ["apple", "banana", "orange", "strawberry", "grape"],
    "yue": ["蘋果", "香蕉", "橙", "草莓", "提子"],
    "cmn": ["苹果", "香蕉", "橙子", "草莓", "葡萄"]
}

SAMPLE_RATE = 16000
CHANNELS = 1
DURATION = 5

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_random_fruit', methods=['POST'])
def get_random_fruit():
    data = request.get_json()
    language = data.get("language", "en")
    fruit_name = random.choice(FRUITS.get(language, FRUITS["en"]))
    return jsonify({"fruit_name": fruit_name})

@app.route('/record_pronunciation', methods=['POST'])
def record_pronunciation():
    data = request.get_json()
    language = data.get("language", "en")
    target_fruit = data.get("target_fruit", "")

    # Start recording timer
    record_start_time = time.time()
    
    # Record audio
    audio_data = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int16')
    sd.wait()
    record_end_time = time.time()
    
    # Calculate recording duration
    record_duration = round(record_end_time - record_start_time, 2)

    # Save the audio to a temporary file
    with wave.open("temp_audio.wav", "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # 16-bit audio
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_data.tobytes())

    # Start processing timer
    process_start_time = time.time()

    # Read audio file bytes
    with open("temp_audio.wav", "rb") as audio_file:
        audio_bytes = audio_file.read()

    # Transcribe using Gladia API
    headers = {"x-gladia-key": API_KEY}
    files = {'audio': ("temp_audio.wav", audio_bytes, 'audio/wav')}
    params = {"language": language, "no_spelling_correction": True}

    response = requests.post(GLADIA_API_URL, headers=headers, files=files, params=params)
    process_end_time = time.time()
    process_duration = round(process_end_time - process_start_time, 2)

    if response.status_code == 200:
        transcription = response.json().get("prediction", [{}])[0].get("transcription", "")
        
        if transcription.lower() == target_fruit.lower():
            feedback = "Great! Your pronunciation is correct."
        else:
            feedback = f"Incorrect. You said '{transcription}'. The correct pronunciation is '{target_fruit}'."
        
        return jsonify({
            "transcription": transcription,
            "feedback": feedback,
            "record_time": record_duration,
            "process_time": process_duration
        })
    else:
        return jsonify({"error": f"Transcription failed: {response.status_code} - {response.text}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
