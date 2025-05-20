from pytubefix import YouTube
from pytubefix.cli import on_progress
from moviepy import AudioFileClip
import os
import speech_recognition as sr
import google.generativeai as genai
import time

# Classe para representar um vídeo do YouTube
class Video:
    def __init__(self, url):
        self.url = url

    # Método para baixar apenas o áudio do vídeo
    def baixar_audio(self):
        yt = YouTube(self.url, on_progress_callback=on_progress)  # Cria objeto YouTube e define callback de progresso
        print(yt.title)

        ys = yt.streams.get_audio_only()  # Seleciona apenas o stream de áudio
        ys.download("Áudios Baixados/", yt.title + ".mp4")  # Faz download do áudio
        path = os.path.join("Áudios Baixados", yt.title + ".mp4")  # Caminho do arquivo baixado
        print("Download completo!")

        return path # Retorna o caminho do arquivo de áudio
    
#     def duration(self):
#         yt = YouTube(self.url)
#         return yt.length

# def cronometro(duração):
#     inicio = 0
#     while inicio < duração:
#         time.sleep(1)
#         inicio += 1

# URL do vídeo a ser analisado
url = "https://www.youtube.com/watch?v=9tjrb3D8b1A&ab_channel=AugustoGalego"
video1 = Video(url)
# duration = video1.duration()

# Cria a pasta para áudios baixados, se não existir
if not os.path.exists("Áudios Baixados"):
    os.mkdir("Áudios Baixados")

# Baixa o áudio do vídeo
arquivo_m4a = video1.baixar_audio()

# Converte o áudio baixado para WAV (necessário para o reconhecimento de fala)
audio = AudioFileClip(arquivo_m4a)
audio.write_audiofile("temporario.wav", codec='pcm_s16le')
audio_clipt = AudioFileClip("temporario.wav")
duracao_total = int(audio_clipt.duration)

# Inicializa o reconhecedor de fala
reconhecedor = sr.Recognizer()
texto_list = []

with sr.AudioFile("temporario.wav") as source:
    print("Lendo Áudio")
    for i in range(0, duracao_total, 30):
        try:
            print(f"Lendo trecho de {i} a {min(i+30, duracao_total)} segundos")
            dados_audio = reconhecedor.record(source, duration=30)
            texto = reconhecedor.recognize_google(dados_audio, language="pt-BR")
            texto_list.append(texto)
        except sr.UnknownValueError:
            texto_list.append("[Inaudível]")
        except sr.RequestError as e:
            texto_list.append(f"[Erro na API: {e}]")

texto_str = "\n".join(texto_list)
# print(texto_str)    

#Configura a API do Gemini com a chave de acesso
genai.configure(api_key='Your API KEY here')
modelo = genai.GenerativeModel("gemini-2.0-flash-lite")
# Gera um resumo do texto transcrito usando o Gemini
resposta = modelo.generate_content(
    f"O seguinte texto é uma transcrição sobre um vídeo do Youtube, retorne um resumo sobre esse vídeo:\n\n{texto_str}"
)

print("\n---Análise pelo Gemini---")
print(resposta.text)