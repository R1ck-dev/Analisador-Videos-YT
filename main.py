from pytubefix import YouTube
from pytubefix.cli import on_progress
from moviepy import AudioFileClip
import os
import speech_recognition as sr
import google.generativeai as genai
import ffmpeg

# Classe para representar um vídeo do YouTube
class Video:
    def __init__(self, url):
        self.url = url

    # Método para baixar apenas o áudio do vídeo
    def baixar_audio(self, pasta_destino="Áudios Baixados"):
        yt = YouTube(self.url, on_progress_callback=on_progress)
        print(f"Título do vídeo: {yt.title}")
        if not os.path.exists(pasta_destino):
            os.mkdir(pasta_destino)
        ys = yt.streams.get_audio_only()
        nome_arquivo = yt.title + ".mp4"
        ys.download(pasta_destino, nome_arquivo)
        path = os.path.join(pasta_destino, nome_arquivo)
        print("Download completo!")
        return path

def converter_para_wav(arquivo_entrada, arquivo_saida="temporario.wav"):
    # Converte o áudio baixado para WAV usando ffmpeg
    ffmpeg.input(arquivo_entrada).output(
        arquivo_saida, acodec='pcm_s16le', ac=1, ar='16000'
    ).run(overwrite_output=True)
    return arquivo_saida

def transcrever_audio(wav_path):
    # Divide o áudio em blocos de 30s e transcreve cada um
    audio_clipt = AudioFileClip(wav_path)
    duracao_total = int(audio_clipt.duration)
    reconhecedor = sr.Recognizer()
    texto_list = []
    with sr.AudioFile(wav_path) as source:
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
    return "\n".join(texto_list)

def resumir_com_gemini(texto):
    # Configura a API do Gemini e gera um resumo
    genai.configure(api_key='Your API key here')
    modelo = genai.GenerativeModel("gemini-2.0-flash-lite")
    resposta = modelo.generate_content(
        f"O seguinte texto é uma transcrição sobre um vídeo do Youtube, retorne um resumo sobre esse vídeo:\n\n{texto}"
    )
    return resposta.text

if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=eSEO1DR_V_Y"
    video1 = Video(url)
    arquivo_m4a = video1.baixar_audio()
    wav_path = converter_para_wav(arquivo_m4a)
    texto_str = transcrever_audio(wav_path)
    resumo = resumir_com_gemini(texto_str)
    print("\n---Análise pelo Gemini---")
    print(resumo)