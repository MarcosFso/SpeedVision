
from datetime import datetime

def atualizar_resultados(resultados, veiculo):
    vid = veiculo["id"]
    vel = veiculo.get("velocidade", 0)

    if vid not in resultados:
        resultados[vid] = {
            "id": vid,
            "tipo": veiculo["tipo"],
            "sentido": veiculo["sentido"],
            "velocidade_maxima": 0,
            "soma": 0,
            "qtd": 0,
        }

    r = resultados[vid]
    if vel > 0:
        r["qtd"] += 1
        r["soma"] += vel
        r["velocidade_maxima"] = max(r["velocidade_maxima"], vel)

def nome_infracao(vid, velocidade):
    return f"ID{vid}_{int(velocidade)}kmh_{datetime.now():%Y%m%d_%H%M%S}.jpg"
