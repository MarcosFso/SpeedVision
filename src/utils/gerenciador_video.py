import os

import yt_dlp


def garantir_video_local(url_youtube, nome_arquivo_local="videos/video_trafego.mp4"):
    os.makedirs(os.path.dirname(nome_arquivo_local), exist_ok=True)

    if os.path.exists(nome_arquivo_local):
        print("Video encontrado localmente. Rodando OFFLINE!")
        return nome_arquivo_local

    print("[DOWNLOAD] Baixando o video de testes...")
    opcoes_download = {
        "format": "best[ext=mp4]",
        "outtmpl": nome_arquivo_local,
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(opcoes_download) as ydl:
        ydl.download([url_youtube])

    print(f"[SUCESSO] Salvo como '{nome_arquivo_local}'.")
    return nome_arquivo_local
