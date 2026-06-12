import cv2


class DesignerRadar:
    @staticmethod
    def desenhar_texto(frame, texto, posicao, escala=0.55, cor=(255, 255, 255), espessura=1):
        x, y = posicao

        cv2.putText(
            frame,
            texto,
            (x + 1, y + 1),
            cv2.FONT_HERSHEY_SIMPLEX,
            escala,
            (0, 0, 0),
            espessura + 2,
            cv2.LINE_AA,
        )

        cv2.putText(
            frame,
            texto,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            escala,
            cor,
            espessura,
            cv2.LINE_AA,
        )

    @staticmethod
    def desenhar_limites_pistas(frame):
        cv2.line(frame, (0, 350), (540, 350), (0, 0, 255), 2)
        DesignerRadar.desenhar_texto(frame, "FIM", (15, 340), 0.45, (0, 0, 255), 1)

        cv2.line(frame, (0, 650), (540, 650), (0, 255, 0), 2)
        DesignerRadar.desenhar_texto(frame, "INICIO", (15, 640), 0.45, (0, 255, 0), 1)

        cv2.line(frame, (540, 350), (1080, 350), (0, 255, 0), 2)
        DesignerRadar.desenhar_texto(frame, "INICIO", (555, 340), 0.45, (0, 255, 0), 1)

        cv2.line(frame, (540, 650), (1080, 650), (0, 0, 255), 2)
        DesignerRadar.desenhar_texto(frame, "FIM", (555, 640), 0.45, (0, 0, 255), 1)

    @staticmethod
    def desenhar_veiculos(frame, dados_veiculos):
        for veiculo in dados_veiculos:
            x, y = veiculo["x"], veiculo["y"]
            v_id = veiculo["id"]
            v_tipo = veiculo["tipo"].upper()
            v_sentido = veiculo["sentido"]

            velocidade = veiculo.get("velocidade", 0)
            acima_limite = veiculo.get("acima_limite", False)

            cor_ponto = (255, 255, 0) if v_sentido == "vindo" else (255, 0, 255)
            cor_texto = (0, 0, 255) if acima_limite else (0, 255, 255)

            cv2.circle(frame, (x, y), 5, cor_ponto, -1)

            texto_etiqueta = f"{v_tipo} #{v_id}"
            texto_velocidade = (
                f"{velocidade:.1f} km/h"
                if velocidade > 0
                else "calculando..."
            )

            DesignerRadar.desenhar_texto(
                frame,
                texto_etiqueta,
                (x + 10, y - 12),
                0.45,
                cor_texto,
                1,
            )

            DesignerRadar.desenhar_texto(
                frame,
                texto_velocidade,
                (x + 10, y + 8),
                0.45,
                cor_texto,
                1,
            )

        # Borda vermelha quando houver infrator
        tem_infrator = any(
            v.get("acima_limite", False)
            for v in dados_veiculos
        )

        if tem_infrator:
            cv2.rectangle(
                frame,
                (0, 0),
                (1080, 720),
                (0, 0, 255),
                15
            )

    @staticmethod
    def desenhar_painel_resultados(frame, resumo):
        # Painel removido completamente
        return frame