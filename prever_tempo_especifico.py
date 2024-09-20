import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder, StandardScaler
import sys
import warnings
warnings.filterwarnings('ignore')

# Função para prever o tempo estimado com dados específicos
def prever_tempo_estimado(local_partida, destino_entrega, distancia, condicoes_trafego):
    with open('pkl_eficiencia_rotas.pkl', 'rb') as file:
        modelo = pickle.load(file)
    
    # Carregar os dados do arquivo CSV
    dados = pd.read_csv('entregas_data.csv')
    # Reaplicar o Label Encoding nas colunas categóricas
    
    label_encoders = {}
    for column in ['Local de Partida', 'Destino da Entrega', 'Condições de Tráfego']:
        le = LabelEncoder()
        dados[column] = le.fit_transform(dados[column])
        label_encoders[column] = le
    
    # Normalizar a Distância (utilize o mesmo StandardScaler usado no treinamento)
    scaler = StandardScaler()
    dados[['Distância']] = scaler.fit_transform(dados[['Distância']])
    
    # Codificar os valores fornecidos
    local_partida_encoded = label_encoders['Local de Partida'].transform([local_partida])[0]
    destino_entrega_encoded = label_encoders['Destino da Entrega'].transform([destino_entrega])[0]
    condicoes_trafego_encoded = label_encoders['Condições de Tráfego'].transform([condicoes_trafego])[0]
    
    # Criar DataFrame para os dados fornecidos
    dados_fornecidos = pd.DataFrame({
        'Local de Partida': [local_partida_encoded],
        'Destino da Entrega': [destino_entrega_encoded],
        'Distância': [scaler.transform([[distancia]])[0][0]],
        'Condições de Tráfego': [condicoes_trafego_encoded]
    })
    
    # Prever o tempo estimado
    tempo_estimado = modelo.predict(dados_fornecidos)
    
    print(tempo_estimado[0].round(2))
    
    return tempo_estimado[0]

if __name__ == "__main__":
    
    local_partida = sys.argv[1]
    destino_entrega = sys.argv[2]
    distancia = float(sys.argv[3])
    condicoes_trafego = sys.argv[4]
    
    #local_partida = 'CD1'
    #destino_entrega = 'Local A'
    #distancia = 50
    #condicoes_trafego = 'Baixo'

    # Prever o tempo estimado
    tempo_estimado = prever_tempo_estimado(local_partida, destino_entrega, distancia, condicoes_trafego)
    tempo_estimado = tempo_estimado.round(2)
    
    