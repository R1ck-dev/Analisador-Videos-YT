from pytubefix import YouTube
from pytubefix.cli import on_progress
from moviepy import AudioFileClip
import os
import speech_recognition as sr
import google.generativeai as genai

class Video:
    def __init__(self, url):
        self.url = url

    def baixar_audio(self):
        yt = YouTube(self.url, on_progress_callback=on_progress)
        print(yt.title)

        ys = yt.streams.get_audio_only()
        ys.download("Áudios Baixados/", yt.title + ".mp4")
        path = os.path.join("Áudios Baixados", yt.title + ".mp4")
        print("Download completo!")

        return path

url = "https://www.youtube.com/shorts/k9oC_WVhFCI"
video1 = Video(url)

if not os.path.exists("Áudios Baixados"):
    os.mkdir("Áudios Baixados")

arquivo_m4a = video1.baixar_audio()

audio = AudioFileClip(arquivo_m4a)
audio.write_audiofile("temporario.wav", codec='pcm_s16le')

reconhecedor = sr.Recognizer()
with sr.AudioFile("temporario.wav") as source:
    print("Lendo Áudio")
    dados_audio = reconhecedor.record(source)
    texto = reconhecedor.recognize_google(dados_audio, language="pt-BR")
    print("Transcrição")
    print(texto)

genai.configure(api_key='AIzaSyAQbeWmC6Z9dEg6oJQA1Ovf9MitaNB7NRw')
modelo = genai.GenerativeModel("gemini-2.0-flash-lite")
resposta = modelo.generate_content(
    f"O seguinte texto é uma transcrição sobre um vídeo do Youtube, retorne um resumo sobre esse vídeo:\n\n{texto}"
)

print("\n---Análise pelo Gemini---")
print(resposta.text)