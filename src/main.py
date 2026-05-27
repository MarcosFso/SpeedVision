import cv2  
# Importa as funções e classes que criamos nos outros arquivos da pasta 'utils'
from utils.gerenciador_video import garantir_video_local
from utils.detector import LocalizadorVeiculos  
from utils.interface import DesignerRadar

def executar_radar():
    # Link do YouTube usado para a base de testes do tráfego
    link_youtube = "https://www.youtube.com/watch?v=PNCJQkvALVc"
    
    # Executa a função que garante o vídeo baixado e o carrega no leitor de vídeo do OpenCV
    caminho_video = garantir_video_local(link_youtube)
    captura = cv2.VideoCapture(caminho_video)
    
    # Inicializa a classe de localização de veículos (YOLO)
    detector = LocalizadorVeiculos()
    
    contador_frames = 0 # Inicializa um contador para controlar o fluxo de processamento
    dados_veiculos = []  # Cria uma lista persistente de veículos
    
    # Loop principal que roda frame por frame enquanto o vídeo estiver aberto
    while captura.isOpened():
        sucesso, frame = captura.read() # Captura a imagem do frame atual
        
        # Se o vídeo acabar ou falhar, reinicia ele automaticamente do frame zero (Loop infinito)
        if not sucesso:
            captura.set(cv2.CAP_PROP_POS_FRAMES, 0) 
            continue
            
        # Redimensiona o tamanho da imagem do frame para um padrão leve de 1080x720 pixels
        frame_ajustado = cv2.resize(frame, (1080, 720))
        
        # 1. Desenha as linhas horizontais de INÍCIO e FIM nas pistas (Chama o designer)
        DesignerRadar.desenhar_limites_pistas(frame_ajustado)
        
        # 2. Otimização de Performance: Roda a detecção pesada da IA apenas a cada 2 frames
        if contador_frames % 2 == 0:
            dados_veiculos = detector.detectar_e_rastrear(frame_ajustado)
            
        contador_frames += 1 # Incrementa o nosso contador de controle
        
        # 3. Desenha as marcações das bolinhas e IDs limpos nos veículos válidos
        DesignerRadar.desenhar_veiculos(frame_ajustado, dados_veiculos)
            
        # Abre a janela visual na tela do computador mostrando o resultado em tempo real
        cv2.imshow("Radar de Velocidade - SpeedVision AI (OFFLINE)", frame_ajustado)
        
        # Monitora o teclado: Se o usuário apertar 'ESC' (código 27) ou 'q', fecha o sistema
        tecla = cv2.waitKey(20) & 0xFF
        if tecla == 27 or tecla == ord('q'):
            break
            
    # Fecha o arquivo de vídeo e encerra todas as janelas gráficas do computador para limpar a memória RAM
    captura.release()
    cv2.destroyAllWindows()

# Garante que o script só vai iniciar se ele for executado diretamente pelo terminal
if __name__ == "__main__":
    executar_radar()