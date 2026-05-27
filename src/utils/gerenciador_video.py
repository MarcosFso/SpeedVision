import os
import yt_dlp

def garantir_video_local(url_youtube, nome_arquivo_local="video_trafego.mp4"):
    # Verifica se o arquivo do vídeo já existe na pasta do projeto
    if os.path.exists(nome_arquivo_local):
        print(f"Vídeo encontrado localmente. Rodando OFFLINE!")
        return nome_arquivo_local # Retorna o caminho do vídeo local e pula o download, pois já tem instalado

    print("[DOWNLOAD] Baixando o vídeo de testes...")
    # Configurações do yt_dlp para baixar em formato MP4
    opcoes_download = {
        'format': 'best[ext=mp4]', 
        'outtmpl': nome_arquivo_local,  
        'quiet': True,                  
        'no_warnings': True
    }
    # Abre o gerenciador de downloads e baixa o vídeo do link do YouTube
    with yt_dlp.YoutubeDL(opcoes_download) as ydl:
        ydl.download([url_youtube])
    print(f"[SUCESSO] Salvo como '{nome_arquivo_local}'.")
    return nome_arquivo_local # Retorna o arquivo baixado