import os
import csv
import threading
import time

import cv2
from flask import Flask, Response, jsonify, render_template, send_file, request, abort

from utils.detector import LocalizadorVeiculos
from utils.fisica import MotorFisicoRadar
from utils.gerenciador_video import garantir_video_local
from utils.interface import DesignerRadar
from flask import send_from_directory


# ============================================================
# CONFIGURACOES GERAIS
# ============================================================
LINK_YOUTUBE = "https://www.youtube.com/watch?v=PNCJQkvALVc"
LARGURA_FRAME = 1080
ALTURA_FRAME = 720
METROS_POR_PIXEL = 0.08
VELOCIDADE_MAXIMA_VALIDA = 220
PROJETO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.dirname(os.path.abspath(__file__))

PASTA_INFRACOES = os.path.join(PROJETO_DIR, "infracoes")
ARQUIVO_RELATORIO = os.path.join(SRC_DIR, "relatorio_radar.csv")

app = Flask(__name__)


# ============================================================
# ESTADO GLOBAL COMPARTILHADO (entre a thread do radar e a API)
# ============================================================
class EstadoRadar:
    def __init__(self):
        self.lock = threading.Lock()
        self.rodando = False
        self.thread = None

        self.frame_atual = None  # frame JPEG (bytes) mais recente
        self.resultados_finais = {}
        self.resumo = {
            "total": 0,
            "com_velocidade": 0,
            "media": 0,
            "maior": 0,
            "acima_limite": 0,
            "limite": 80,
        }
        self.limite_velocidade_kmh = 80

    def get_frame(self):
        with self.lock:
            return self.frame_atual

    def set_frame(self, frame_bytes):
        with self.lock:
            self.frame_atual = frame_bytes

    def get_resumo(self):
        with self.lock:
            return dict(self.resumo)

    def get_limite(self):
        with self.lock:
            return self.limite_velocidade_kmh

    def set_limite(self, novo_limite):
        with self.lock:
            self.limite_velocidade_kmh = novo_limite
            self.resumo["limite"] = novo_limite


estado = EstadoRadar()


# ============================================================
# LOGICA DO RADAR (adaptada do main.py original, sem cv2.imshow)
# ============================================================
def atualizar_resultados(resultados_finais, veiculo):
    v_id = veiculo["id"]
    velocidade = veiculo.get("velocidade", 0)

    if v_id not in resultados_finais:
        resultados_finais[v_id] = {
            "id": v_id,
            "tipo": veiculo["tipo"],
            "sentido": veiculo["sentido"],
            "velocidade_atual": 0,
            "velocidade_maxima": 0,
            "leituras": [],
        }

    resultado = resultados_finais[v_id]
    resultado["tipo"] = veiculo["tipo"]
    resultado["sentido"] = veiculo["sentido"]
    resultado["velocidade_atual"] = velocidade

    if velocidade > 0:
        resultado["leituras"].append(velocidade)
        resultado["velocidade_maxima"] = max(resultado["velocidade_maxima"], velocidade)


def compilar_resumo(resultados_finais, limite_velocidade_kmh):
    total_monitorados = len(resultados_finais)
    veiculos_com_velocidade = [
        item for item in resultados_finais.values() if item["leituras"]
    ]
    velocidades = [
        leitura for item in veiculos_com_velocidade for leitura in item["leituras"]
    ]

    if velocidades:
        velocidade_media = sum(velocidades) / len(velocidades)
        maior_velocidade = max(velocidades)
    else:
        velocidade_media = 0
        maior_velocidade = 0

    acima_limite = sum(
        1
        for item in veiculos_com_velocidade
        if item["velocidade_maxima"] > limite_velocidade_kmh
    )

    return {
        "total": total_monitorados,
        "com_velocidade": len(veiculos_com_velocidade),
        "media": round(velocidade_media, 1),
        "maior": round(maior_velocidade, 1),
        "acima_limite": acima_limite,
        "limite": limite_velocidade_kmh,
    }


def exportar_csv(resultados_finais, limite_velocidade_kmh):
    with open(ARQUIVO_RELATORIO, mode="w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(
            ["ID do Veiculo", "Tipo", "Sentido", "Velocidade Maxima (km/h)", "Multado?"]
        )

        for v_id, dados in resultados_finais.items():
            if dados["velocidade_maxima"] > 0:
                multado = "SIM" if dados["velocidade_maxima"] > limite_velocidade_kmh else "NAO"
                vel_max = round(dados["velocidade_maxima"], 1)
                escritor.writerow([v_id, dados["tipo"], dados["sentido"], vel_max, multado])


def loop_radar():
    caminho_video = garantir_video_local(LINK_YOUTUBE)
    captura = cv2.VideoCapture(caminho_video)

    if not captura.isOpened():
        print(f"[ERRO] Nao foi possivel abrir o video: {caminho_video}")
        with estado.lock:
            estado.rodando = False
        return

    fps_video = captura.get(cv2.CAP_PROP_FPS) or 30
    detector = LocalizadorVeiculos()
    motor_fisico = MotorFisicoRadar(fps_video, METROS_POR_PIXEL)

    contador_frames = 0
    dados_veiculos = []
    resultados_finais = {}

    while True:
        with estado.lock:
            if not estado.rodando:
                break
            limite_atual = estado.limite_velocidade_kmh

        sucesso, frame = captura.read()

        if not sucesso:
            # Reinicia o video do comeco (loop continuo)
            captura.set(cv2.CAP_PROP_POS_FRAMES, 0)
            contador_frames = 0
            continue

        frame_ajustado = cv2.resize(frame, (LARGURA_FRAME, ALTURA_FRAME))
        DesignerRadar.desenhar_limites_pistas(frame_ajustado)

        tempo_atual = contador_frames / fps_video

        if contador_frames % 2 == 0:
            dados_veiculos = detector.detectar_e_rastrear(frame_ajustado)

            for veiculo in dados_veiculos:
                velocidade = motor_fisico.calcular_velocidade(veiculo, tempo_atual)
                if velocidade > VELOCIDADE_MAXIMA_VALIDA:
                    velocidade = 0

                veiculo["velocidade"] = velocidade
                veiculo["acima_limite"] = velocidade > limite_atual
                atualizar_resultados(resultados_finais, veiculo)

                # ================= FLASH DO RADAR =================
                if veiculo["acima_limite"]:
                    os.makedirs(PASTA_INFRACOES, exist_ok=True)
                    nome_foto = os.path.join(
                        PASTA_INFRACOES, f"ID{veiculo['id']}_{velocidade}kmh.jpg"
                    )

                    if not os.path.exists(nome_foto):
                        x, y = veiculo["x"], veiculo["y"]
                        y1, y2 = max(0, y - 60), min(ALTURA_FRAME, y + 60)
                        x1, x2 = max(0, x - 60), min(LARGURA_FRAME, x + 60)

                        foto_recortada = frame_ajustado[y1:y2, x1:x2]
                        if foto_recortada.size > 0:
                            cv2.imwrite(nome_foto, foto_recortada)
                # ====================================================

        contador_frames += 1

        resumo = compilar_resumo(resultados_finais, limite_atual)
        DesignerRadar.desenhar_veiculos(frame_ajustado, dados_veiculos)
        DesignerRadar.desenhar_painel_resultados(frame_ajustado, resumo)

        ok, buffer = cv2.imencode(".jpg", frame_ajustado)
        if ok:
            estado.set_frame(buffer.tobytes())

        with estado.lock:
            estado.resultados_finais = resultados_finais
            estado.resumo = resumo

        # Atualiza o CSV periodicamente para o botao de download
        if contador_frames % 30 == 0:
            exportar_csv(resultados_finais, limite_atual)

        time.sleep(1 / fps_video)

    captura.release()
    exportar_csv(resultados_finais, limite_atual)
    print("[INFO] Loop do radar finalizado.")


# ============================================================
# ROTAS DA PAGINA
# ============================================================
@app.route("/")
def index():
    return render_template("index.html")


# ============================================================
# STREAM DE VIDEO (MJPEG)
# ============================================================
def gerar_stream():
    while True:
        frame = estado.get_frame()
        if frame is not None:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )
        time.sleep(0.03)


@app.route("/video_feed")
def video_feed():
    return Response(
        gerar_stream(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# ============================================================
# API - ESTATISTICAS
# ============================================================
@app.route("/api/resumo")
def api_resumo():
    resumo = estado.get_resumo()
    with estado.lock:
        resumo["rodando"] = estado.rodando
    return jsonify(resumo)


# ============================================================
# API - CONTROLES (iniciar / parar / limite de velocidade)
# ============================================================
@app.route("/api/controle/iniciar", methods=["POST"])
def api_iniciar():
    with estado.lock:
        if estado.rodando:
            return jsonify({"status": "ja_rodando"})
        estado.rodando = True
        estado.thread = threading.Thread(target=loop_radar, daemon=True)
        estado.thread.start()
    return jsonify({"status": "iniciado"})


@app.route("/api/controle/parar", methods=["POST"])
def api_parar():
    with estado.lock:
        estado.rodando = False
    return jsonify({"status": "parando"})


@app.route("/api/controle/limite", methods=["POST"])
def api_limite():
    dados = request.get_json(silent=True) or {}
    try:
        novo_limite = float(dados.get("limite"))
    except (TypeError, ValueError):
        return jsonify({"erro": "limite invalido"}), 400

    estado.set_limite(novo_limite)
    return jsonify({"status": "ok", "limite": novo_limite})


# ============================================================
# API - INFRACOES (galeria de fotos)
# ============================================================
@app.route("/api/infracoes")
def api_infracoes():
    if not os.path.isdir(PASTA_INFRACOES):
        return jsonify([])

    itens = []
    for nome_arquivo in sorted(os.listdir(PASTA_INFRACOES)):
        if not nome_arquivo.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        # Espera o formato: ID<id>_<velocidade>kmh.jpg
        info = {"arquivo": nome_arquivo, "id": None, "velocidade": None}
        try:
            base = nome_arquivo.rsplit(".", 1)[0]
            partes = base.split("_")
            info["id"] = partes[0].replace("ID", "")
            info["velocidade"] = partes[1].replace("kmh", "")
        except (IndexError, ValueError):
            pass

        itens.append(info)

    itens.reverse()  # mais recentes primeiro
    return jsonify(itens)

@app.route("/infracoes/<path:nome_arquivo>")
def servir_infracao(nome_arquivo):
    return send_from_directory(PASTA_INFRACOES, nome_arquivo)

# ============================================================
# API - RELATORIO CSV
# ============================================================
@app.route("/api/relatorio")
def api_relatorio():
    with estado.lock:
        resultados = dict(estado.resultados_finais)
        limite = estado.limite_velocidade_kmh

    exportar_csv(resultados, limite)

    if not os.path.isfile(ARQUIVO_RELATORIO):
        abort(404)

    return send_file(
        ARQUIVO_RELATORIO,
        mimetype="text/csv",
        as_attachment=True,
        download_name="relatorio_radar.csv",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
