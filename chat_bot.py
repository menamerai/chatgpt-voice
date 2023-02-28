from dotenv import dotenv_values
from revChatGPT.V1 import Chatbot
import pyaudio
import whisper
import wave

config = dotenv_values(".env")

chatgpt = Chatbot(config={
    "access_token": config["ACCESS_TOKEN"],
})

while True:
    directive = input("Enter a directive(r/q): ")
    if directive == "q":
        break
    elif directive == "r":
        # Record audio
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 1024
        RECORD_SECONDS = 5
        WAVE_OUTPUT_FILENAME = "output.wav"
        stream = pyaudio.PyAudio().open(format=FORMAT, channels=CHANNELS,
                                        rate=RATE, input=True,  
                                        frames_per_buffer=CHUNK)
        print("recording...")
        frames = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        print("finished recording")
        stream.stop_stream()
        stream.close()
        pyaudio.PyAudio().terminate()

        waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        waveFile.setnchannels(CHANNELS)
        waveFile.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
        waveFile.setframerate(RATE)
        waveFile.writeframes(b''.join(frames))
        waveFile.close()
        

