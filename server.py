import openai
import time
import serial
import subprocess
import os
import soundfile as sf
import uuid
import io
from openai import OpenAI
from pydub import AudioSegment 
import tempfile
import platform


client = OpenAI(api_key="YOUR_API_KEY")

# CONFIG
SERIAL_PORT = "COM4"
BAUD_RATE = 115200
TTS_VOICE = "nova"

# SERIAL SETUP
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # Allow Arduino to reset

def record_audio(filename="input.wav"):
    print("🎤 Recording...")
    import sounddevice as sd
    duration = 5
    samplerate = 16000
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
    sd.wait()
    sf.write(filename, recording, samplerate)
    print("✅ Recording saved.")

def transcribe_with_openai(audio_file):
    print("🧠 Transcribing...")
    with open(audio_file, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
    return transcript.text

def get_openai_chat_response(prompt):
    print("🤖 ChatGPT responding...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def synthesize_openai_tts_to_memory(text):
    print("🎙️ Generating TTS (mp3)...")
    response = client.audio.speech.create(
        model="tts-1",
        voice=TTS_VOICE,
        input=text
    )
    return io.BytesIO(response.content)  # MP3 in memory




def play_openai_tts_on_laptop(mp3_bytes_io):
    print("🔊 Playing TTS on laptop speakers...")

    # Save MP3 to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
        temp_audio_file.write(mp3_bytes_io.read())
        temp_path = temp_audio_file.name

    # Use built-in player based on OS
    system = platform.system()
    if system == "Windows":
        os.system(f'start "" "{temp_path}"')
    elif system == "Darwin":  # macOS
        os.system(f'afplay "{temp_path}"')
    elif system == "Linux":
        os.system(f'xdg-open "{temp_path}"')
    else:
        print("❌ Unsupported OS for audio playback.")



def split_lines(prefix, text, line_length):
    lines = [f"{prefix}:{text[i:i+line_length]}" for i in range(0, len(text), line_length)]
    return lines

# === Send lines over serial to Arduino ===
def send_Q_oled(lines):
    print("sent to oled:")
    for line in lines:
        ser.write((line + '\n').encode('utf-8'))
        time.sleep(0.5)  # Give Arduino time to process
        print(line)

    # ✅ Send "DONE" to signal the end of the transmission
    ser.write(b"DONE\n")
    print("✅ Sent DONE to signal OLED update.")

       


def main():
    while True:
        input("🎙️ Press ENTER to record...")

        audio_file = f"input_{uuid.uuid4().hex}.wav"
        record_audio(audio_file)

        try:
            question = transcribe_with_openai(audio_file)
        except Exception as e:
            print("❌ Transcription failed:", e)
            os.remove(audio_file)
            continue

        print("Question:", question)
        answer = get_openai_chat_response(question)
        print("Answer:", answer)
        # Send question and answer to OLED via serial
        question_lines = split_lines("Q", question, 20)
        answer_lines = split_lines("A", answer, 20) 
        send_Q_oled(question_lines + answer_lines)
        mp3_data_io = synthesize_openai_tts_to_memory(answer)
        play_openai_tts_on_laptop(mp3_data_io)


        


# Change 'COMX' to your Arduino port. On Mac/Linux, it might look like '/dev/ttyUSB0'
if __name__ == "__main__":
    main()
