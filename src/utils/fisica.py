import cv2
import numpy as np
import math

class MotorFisicoRadar:
    def __init__(self, fps_video, fator_escala_metros):
        self.fps = fps_video 
        self.metros_por_pixel = fator_escala_metros
        self.historico_carros = {}
        self.matriz = None 

    def obter_matriz_perspectiva(self, pts_origem, largura_real, altura_real):
        # Mapeia os pontos da camera para uma visao top-down (zera a distorcao)
        pts_src = np.float32(pts_origem)
        pts_dst = np.float32([[0, 0], [largura_real, 0], [largura_real, altura_real], [0, altura_real]])
        
        self.matriz = cv2.getPerspectiveTransform(pts_src, pts_dst)
        return self.matriz

    def transformar_ponto(self, x, y):
        # Aplica a matriz de correcao na coordenada atual
        if self.matriz is None:
            return x, y 
            
        pt = np.float32([[[x, y]]])
        pt_transf = cv2.perspectiveTransform(pt, self.matriz)
        
        return pt_transf[0][0][0], pt_transf[0][0][1]

    def calcular_velocidade(self, veiculo, tempo_atual):
        v_id = veiculo["id"]
        x_atual, y_atual = self.transformar_ponto(veiculo["x"], veiculo["y"])
        velocidade_kmh = 0.0

        # Verifica se o carro ja foi registrado antes para calcular o delta
        if v_id in self.historico_carros:
            x_antigo = self.historico_carros[v_id]["x"]
            y_antigo = self.historico_carros[v_id]["y"]
            tempo_antigo = self.historico_carros[v_id]["tempo"]

            # Calcula distancia euclidiana em pixels e converte para metros
            distancia_px = math.dist([x_atual, y_atual], [x_antigo, y_antigo])
            distancia_m = distancia_px * self.metros_por_pixel
            
            dt = tempo_atual - tempo_antigo

            if dt > 0:
                v_ms = distancia_m / dt
                velocidade_kmh = round(v_ms * 3.6, 2) # Conversao m/s -> km/h
                
        # Atualiza o frame atual no historico
        self.historico_carros[v_id] = {"x": x_atual, "y": y_atual, "tempo": tempo_atual}
        
        return velocidade_kmh

