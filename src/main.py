import cv2

from utils.detector import LocalizadorVeiculos
from utils.fisica import MotorFisicoRadar
from utils.gerenciador_video import garantir_video_local
from utils.interface import DesignerRadar


LINK_YOUTUBE = "https://www.youtube.com/watch?v=PNCJQkvALVc"
LARGURA_FRAME = 1080
ALTURA_FRAME = 720
METROS_POR_PIXEL = 0.08
LIMITE_VELOCIDADE_KMH = 80
VELOCIDADE_MAXIMA_VALIDA = 220


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


def compilar_resumo(resultados_finais):
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
        if item["velocidade_maxima"] > LIMITE_VELOCIDADE_KMH
    )

    return {
        "total": total_monitorados,
        "com_velocidade": len(veiculos_com_velocidade),
        "media": velocidade_media,
        "maior": maior_velocidade,
        "acima_limite": acima_limite,
        "limite": LIMITE_VELOCIDADE_KMH,
    }


def executar_radar():
    caminho_video = garantir_video_local(LINK_YOUTUBE)
    captura = cv2.VideoCapture(caminho_video)

    if not captura.isOpened():
        raise RuntimeError(f"Nao foi possivel abrir o video: {caminho_video}")

    fps_video = captura.get(cv2.CAP_PROP_FPS) or 30
    detector = LocalizadorVeiculos()
    motor_fisico = MotorFisicoRadar(fps_video, METROS_POR_PIXEL)

    contador_frames = 0
    dados_veiculos = []
    resultados_finais = {}

    while captura.isOpened():
        sucesso, frame = captura.read()

        if not sucesso:
            break

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
                veiculo["acima_limite"] = velocidade > LIMITE_VELOCIDADE_KMH
                atualizar_resultados(resultados_finais, veiculo)

        contador_frames += 1

        resumo = compilar_resumo(resultados_finais)
        DesignerRadar.desenhar_veiculos(frame_ajustado, dados_veiculos)
        DesignerRadar.desenhar_painel_resultados(frame_ajustado, resumo)

        cv2.imshow("Radar de Velocidade - SpeedVision AI", frame_ajustado)

        tecla = cv2.waitKey(20) & 0xFF
        if tecla == 27 or tecla == ord("q"):
            break

    captura.release()
    cv2.destroyAllWindows()

    resumo_final = compilar_resumo(resultados_finais)
    print("\n===== RESULTADOS FINAIS - SPEEDVISION =====")
    print(f"Veiculos monitorados: {resumo_final['total']}")
    print(f"Veiculos com velocidade calculada: {resumo_final['com_velocidade']}")
    print(f"Velocidade media: {resumo_final['media']:.1f} km/h")
    print(f"Maior velocidade: {resumo_final['maior']:.1f} km/h")
    print(
        f"Acima do limite ({resumo_final['limite']} km/h): "
        f"{resumo_final['acima_limite']}"
    )


if __name__ == "__main__":
    executar_radar()
