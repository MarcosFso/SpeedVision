import cv2  
from ultralytics import YOLO  

class LocalizadorVeiculos:
    def __init__(self, modelo_path="yolov8n.pt"):
        # Carrega o modelo YOLOv8 Nano na memória
        self.model = YOLO(modelo_path)
        
        # Filtro de classes 2 = Carro  3 = Moto  7 = Caminhão
        self.classes_permitidas = [2, 3, 7] 

        # Define os limites verticais (pixels do eixo Y) por onde o radar opera
        self.Y_LIMITE_INICIO = 350
        self.Y_LIMITE_FIM = 650
        
        # Define o meio exato do vídeo (1080 de largura / 2 = 540) para separar as pistas
        self.X_DIVISAO_PISTA = 540

    def detectar_e_rastrear(self, frame):
        # Roda o rastreador da IA no frame atual com configurações de performance otimizadas
        resultados = self.model.track(
            frame, 
            persist=True,      # Mantém o mesmo ID para o veículo nos frames seguintes
            verbose=False,     # Esconde as mensagens padrão do YOLO no terminal
            classes=self.classes_permitidas, # Filtra para detectar só veículos do nosso interesse
            conf=0.28,         # Só aceita detecções com mais de 28% de certeza
            iou=0.5,           # Evita caixas duplicadas coladas no mesmo carro
            imgsz=480          # Reduz a resolução interna para a IA processar mais rápido
        )
        
        veiculos_detectados = [] # Lista limpa que vai guardar quem está dentro do radar
        
        # Verifica se a IA encontrou alguma caixa (box) e se ela gerou um ID de rastreio válido
        if resultados[0].boxes is not None and resultados[0].boxes.id is not None:
            boxes = resultados[0].boxes.xyxy.cpu().numpy()  # Coordenadas dos cantos da caixa (x1, y1, x2, y2)
            ids = resultados[0].boxes.id.cpu().numpy().astype(int)  # IDs numéricos dos carros
            clss = resultados[0].boxes.cls.cpu().numpy().astype(int)  # Tipo do veículo (classe)
            
            # Loop que roda para cada veículo encontrado na tela
            for box, track_id, cls in zip(boxes, ids, clss):
                x1, y1, x2, y2 = box
                
                # Calcula o centro horizontal (X) do carro e a sua base vertical (Y, onde os pneus tocam o chão)
                x_centro = int((x1 + x2) / 2)
                y_base = int(y2)
                
                # Filtro de Zona: Só aceita o veículo se ele estiver no espaço vertical do radar (entre 350 e 650)
                if self.Y_LIMITE_INICIO <= y_base <= self.Y_LIMITE_FIM:
                    nome_classe = self.model.names[cls] # Converte o número da classe para o nome (ex: 'car')
                    
                    # Lógica de Repartição: Descobre o sentido se baseando no meio da pista (X = 540)
                    if x_centro < self.X_DIVISAO_PISTA:
                        sentido_pista = "vindo" # Lado esquerdo da imagem
                    else:
                        sentido_pista = "indo"  # Lado direito da imagem
                    
                    # Salva os dados mastigados do veículo na nossa lista
                    veiculos_detectados.append({
                        "id": track_id,       
                        "x": x_centro,       
                        "y": y_base,         
                        "tipo": nome_classe,
                        "sentido": sentido_pista
                    })
                    
        return veiculos_detectados # Retorna a lista de carros monitorados para o main.py