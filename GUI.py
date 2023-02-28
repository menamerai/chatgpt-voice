import tkinter as tk
import customtkinter as ctk
import os
import wave
import time
import threading
import pyaudio
import whisper
import dotenv
import gtts
import playsound

from revChatGPT.V1 import Chatbot

# a class called VoiceRecorder that handles recording audio for the GUI. It has a button to start and stop recording, and a label to display the status of the recording.
class VoiceRecorder:
    def __init__(self, config):
        
        self.config = config

        self.whisper_model = whisper.load_model("base")
        self.current_directive = ""
        self.current_answer = ""

        self.chatbot = Chatbot(config={
            "access_token": self.config["ACCESS_TOKEN"],
        })


        self.root = ctk.CTk()
        self.root.title("Voice Recorder")
        self.root.geometry("400x400")
        self.root.resizable(False, False)
        self.chatbot_textarea = ctk.CTkTextbox(master=self.root, wrap="word", width=350, height=300)
        self.chatbot_textarea.insert("0.0", "ChatGPT: ")
        self.chatbot_textarea.pack(padx=10, pady=10)
        self.button = ctk.CTkButton(text="Start Recording", command=self.click_handler, master=self.root)
        self.button.pack()
        self.label = ctk.CTkLabel(text="00:00:00", master=self.root)
        self.label.pack()
        self.recording = False
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        

    def click_handler(self):
        if self.recording:
            self.recording = False
            self.button.configure(text="Start Recording")
            # remove audio.wav if it exists
            if os.path.exists("audio.wav"):
                os.remove("audio.wav")
        else:
            self.recording = True
            self.button.configure(text="Stop Recording")
            self.chatbot_textarea.delete("0.0", "end")
            self.chatbot_textarea.insert("0.0", "ChatGPT: ")
            threading.Thread(target=self.record_audio).start()

    def record_audio(self):
        # record audio if self.recording is True
        # if self.recording is False, stop recording
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        frames = list()
        start_time = time.time()

        while self.recording:
            data = stream.read(1024)
            frames.append(data)
            self.label.configure(text=time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time)))

        self.button.configure(state="disabled")
        stream.stop_stream()
        stream.close()
        audio.terminate()

        wf = wave.open("audio.wav", "wb")
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b"".join(frames))
        wf.close()

        self.current_directive = self.whisper_model.transcribe("audio.wav", fp16=False)["text"]
        print(self.current_directive)
        prev_text = ""
        self.current_answer = ""
        for data in self.chatbot.ask(self.current_directive):
            message = data["message"][len(prev_text):]
            self.chatbot_textarea.insert("end", message)
            prev_text = data["message"]
            self.current_answer += message

        try:
            tts = gtts.gTTS(self.current_answer)
            tts.save("audio.mp3")
            playsound.playsound("audio.mp3")
            playsound.close()
        except:
            pass
        finally:
            if os.path.exists("audio.mp3"):
                os.remove("audio.mp3")

        self.button.configure(state="normal")

    def on_closing(self):
        self.recording = False
        if os.path.exists("audio.wav"):
            os.remove("audio.wav")
        self.root.destroy()



if __name__ == "__main__":
    dotenv.load_dotenv()
    config = dotenv.dotenv_values(".env")
    VoiceRecorder(config)

