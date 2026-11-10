<h1 align="center">🏎️ SpeedVision</h1>

<p align="center">
  Sistema de monitoramento e estimativa de velocidade veicular com Visão Computacional.<br/>
  Simula um radar eletrônico a partir de vídeos de câmeras de rodovias.
</p>

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,opencv,flask,html,css,js&perline=6" />
</p>

---

## 📌 Sobre o projeto

O SpeedVision processa o vídeo de uma rodovia, detecta e acompanha os veículos que passam pela câmera e estima a velocidade de cada um. Cada veículo recebe um ID e é classificado como **acima ou dentro do limite** de velocidade definido. Os dados são enviados por uma API em Flask para um painel web, que mostra o vídeo processado e as estatísticas em tempo real.

Projeto desenvolvido **em equipe** na faculdade (Sistemas de Informação), para aplicar visão computacional, desenvolvimento web e integração entre back-end e front-end.

## ✨ Funcionalidades

- **Detecção e rastreamento de veículos** com YOLO (modelo `yolov8n`) e OpenCV, com ID único para cada veículo.
- **Estimativa de velocidade** a partir do deslocamento do veículo entre os quadros, convertido de pixels para metros por uma escala calibrada.
- **Limite de velocidade configurável** (padrão: 80 km/h), alterável pela API durante a execução.
- **Painel web em tempo real** com vídeo processado e resumo: total de veículos monitorados, velocidade média, maior velocidade e quantidade acima do limite.
- **Galeria de infrações**: foto de cada veículo que ultrapassa o limite, salva com ID e velocidade.
- **Relatório em CSV** para download pela interface, com o ID de cada veículo e seu status.
- **Download automático do vídeo de teste** (via `yt-dlp`) na primeira execução. Depois disso o projeto roda offline.

## 🛠️ Tecnologias

| Camada | Tecnologias |
| --- | --- |
| Visão computacional | Python, OpenCV, YOLO (Ultralytics), NumPy |
| Back-end / API | Flask |
| Front-end | HTML, CSS, JavaScript |
| Vídeo de teste | yt-dlp |

## 🗂️ Estrutura

```text
SpeedVision/
├── src/
│   ├── app.py          # servidor Flask + API + thread do radar
│   ├── main.py         # versão original do radar
│   ├── utils/          # detector, física, interface e gerenciador de vídeo
│   ├── templates/      # páginas HTML
│   └── static/         # CSS e JavaScript
├── videos/             # vídeo de teste
├── requirements.txt
└── yolov8n.pt          # pesos do modelo YOLO
```

## 🚀 Como executar

Pré-requisito: **Python 3** instalado.

```bash
# 1. Clonar o repositório
git clone https://github.com/MarcosFso/SpeedVision.git
cd SpeedVision

# 2. (Opcional) criar um ambiente virtual
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Iniciar o servidor (execute a partir da raiz do projeto)
python src/app.py
```

Depois abra **http://localhost:5000** no navegador e use os controles do painel para iniciar o radar. Na primeira execução o vídeo de teste é baixado automaticamente, então é necessário ter internet.

## 🔌 Endpoints da API

| Rota | Descrição |
| --- | --- |
| `POST /api/controle/limite` | Define o limite de velocidade (JSON: `{"limite": 80}`) |
| `GET /api/infracoes` | Lista as fotos das infrações registradas |
| `GET /api/relatorio` | Gera e baixa o relatório em CSV |

## 🎯 Objetivo

Aplicar na prática lógica de programação, processamento de vídeo, desenvolvimento web e comunicação entre sistemas, simulando um desafio real de engenharia de software.

## 👥 Autoria

Projeto em equipe da faculdade (Sistemas de Informação).
