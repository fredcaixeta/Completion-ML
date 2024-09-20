import json
import subprocess
response = {
  "arquivo": "prever_tempo_especifico.py",
  "parametros": {
    "local_partida": "CD1",
    "destino_entrega": "Local A",
    "distancia": 50,
    "condicoes_transito": "Baixo"
  }
}


data = response


arquivo = data.get("arquivo")
parametros = data.get("parametros", {})

if arquivo == "prever_tempo_especifico.py":
    # Preparar parâmetros para o script
    local_partida = parametros.get("local_partida")
    destino_entrega = parametros.get("destino_entrega")
    distancia = parametros.get("distancia")
    condicoes_transito = parametros.get("condicoes_transito")

    # Chamar o script auxiliar
    result = subprocess.run(
        ['python', arquivo, local_partida, destino_entrega, str(distancia), condicoes_transito],
        capture_output=True,
        text=True,
        timeout=60
    )
    print(result.stdout)