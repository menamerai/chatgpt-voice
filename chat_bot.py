from dotenv import dotenv_values
from revChatGPT.V1 import Chatbot
from playsound import playsound
import pyaudio
import whisper
import wave
import time
import gtts
import os

config = dotenv_values(".env")

chatgpt = Chatbot(config={
    "access_token": config["ACCESS_TOKEN"],
})

whisper_model = whisper.load_model("base")

while True:
    directive = input("Enter a directive(r/q): ")
    if directive == "q":
        break
    elif directive == "r":
        # Record audio for ten seconds
        print("Recording audio...")
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
        frames = []
        for i in range(0, int(16000 / 1024 * 10)):
            data = stream.read(1024)
            frames.append(data)
            # print every second
            if i % 160 == 0:
                print(".", end="", flush=True)

        print()
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf = wave.open("audio.wav", "wb")
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b"".join(frames))
        wf.close()

        # Convert audio to text
        print("User: ")
        result = whisper_model.transcribe("audio.wav", fp16=False)
        print(result["text"])

        print("Chatbot: ")
        prev_text = ""
        whole_text = ""
        for data in chatgpt.ask(
            result["text"],
        ):
            message = data["message"][len(prev_text) :]
            print(message, end="", flush=True)
            prev_text = data["message"]
            whole_text += message
        print()

        # Convert text to audio
        tts = gtts.gTTS(whole_text, lang="en")
        tts.save("audio.mp3")
        try:
            playsound("audio.mp3")
        except Exception as e:
            print(e)
        finally:
            os.remove("audio.mp3")
            os.remove("audio.wav")

