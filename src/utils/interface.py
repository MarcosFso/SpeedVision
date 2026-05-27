import cv2

class DesignerRadar:
    @staticmethod
    def desenhar_limites_pistas(frame):
        # VIA DA ESQUERDA INICIO embaixo / FIM em cima
        cv2.line(frame, (0, 350), (540, 350), (0, 0, 255), 2)
        cv2.putText(frame, "FIM", (15, 340), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        
        cv2.line(frame, (0, 650), (540, 650), (0, 255, 0), 2)
        cv2.putText(frame, "INICIO", (15, 640), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

        # VIA DA DIREITA INICIO em cima / FIM embaixo
        cv2.line(frame, (540, 350), (1080, 350), (0, 255, 0), 2)
        cv2.putText(frame, "INICIO", (555, 340), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        cv2.line(frame, (540, 650), (1080, 650), (0, 0, 255), 2)
        cv2.putText(frame, "FIM", (555, 640), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    @staticmethod
    def desenhar_veiculos(frame, dados_veiculos):
        # Percorre a lista de veículos que o detector encontrou
        for veiculo in dados_veiculos:
            x, y = veiculo["x"], veiculo["y"]
            v_id = veiculo["id"]
            v_tipo = veiculo["tipo"].upper()
            v_sentido = veiculo["sentido"]
            
            cor_ponto = (255, 255, 0) if v_sentido == "vindo" else (255, 0, 255)
            
            # Desenha uma bolinha preenchida no ponto central/roda do veículo
            cv2.circle(frame, (x, y), 5, cor_ponto, -1)
            
            # Formata deixando apenas o ID (ex: CAR #142)
            texto_etiqueta = f"{v_tipo} #{v_id}"
            
            # Escreve o texto ao lado do veículo para sua identificação
            cv2.putText(frame, texto_etiqueta, (x + 10, y - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 2)