# SpeedVision

Sistema de radar com visao computacional para detectar veiculos em video, rastrear IDs, estimar velocidade e exibir os resultados na tela com OpenCV.

## Funcionalidades

- Download automatico do video de teste com `yt-dlp`.
- Deteccao e rastreamento de carros, motos e caminhoes com YOLOv8.
- Calculo aproximado de velocidade por deslocamento entre frames.
- Desenho das linhas de inicio/fim, IDs, velocidades e painel final com `cv2.putText`.
- Impressao do resumo final no terminal ao encerrar o programa.

## Estrutura

```text
SpeedVision/
  src/
    main.py
    baixar_video.py
    utils/
      detector.py
      fisica.py
      gerenciador_video.py
      interface.py
  videos/
  requirements.txt
  README.md
```

## Como executar

1. Crie ou ative um ambiente virtual.
2. Instale as dependencias:

```bash
pip install -r requirements.txt
```

3. Rode o projeto:

```bash
python src/main.py
```

Pressione `q` ou `ESC` para fechar a janela e ver o resumo final no terminal.

## Observacao

A velocidade e uma estimativa baseada em escala aproximada (`METROS_POR_PIXEL`) definida em `src/main.py`. Para uma medicao mais precisa, calibre esse valor usando uma distancia real conhecida no video.
