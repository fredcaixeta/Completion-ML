import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder, StandardScaler
import warnings
warnings.filterwarnings('ignore')

def encontrar_menor_tempo(local_partida, destino_entrega):
    # Carregar os dados do arquivo CSV
    entregas_data = pd.read_csv('entregas_data.csv')

    # Carregar o modelo do arquivo Pickle
    with open('pkl_eficiencia_rotas.pkl', 'rb') as file:
        modelo_carregado = pickle.load(file)

    # Reaplicar o Label Encoding nas colunas categóricas
    label_encoders = {}
    for column in ['Local de Partida', 'Destino da Entrega', 'Condições de Tráfego']:
        le = LabelEncoder()
        entregas_data[column] = le.fit_transform(entregas_data[column])
        label_encoders[column] = le

    # Normalizar a Distância novamente (utilize o mesmo StandardScaler usado no treinamento)
    scaler = StandardScaler()
    entregas_data[['Distância']] = scaler.fit_transform(entregas_data[['Distância']])

    # Codificar os valores que serão consultados
    try:
        cd1_encoded = label_encoders['Local de Partida'].transform([local_partida])[0]
        local_a_encoded = label_encoders['Destino da Entrega'].transform([destino_entrega])[0]
    except ValueError as e:
        return f"Erro: Um dos valores fornecidos ({local_partida}, {destino_entrega}) não foi visto durante o treinamento."

    # Filtrar as rotas
    rotas_cd1_local_a = entregas_data[(entregas_data['Local de Partida'] == cd1_encoded) & 
                                    (entregas_data['Destino da Entrega'] == local_a_encoded)]

    # Prever o tempo estimado para essas rotas
    X_cd1_local_a = rotas_cd1_local_a[['Local de Partida', 'Destino da Entrega', 'Distância', 'Condições de Tráfego']]
    try:
        tempos_preditos = modelo_carregado.predict(X_cd1_local_a)
    except ValueError as e:
        return f"Erro: Um dos valores fornecidos ({local_partida}, {destino_entrega}) não foi visto durante o treinamento."

    # Adicionar as previsões ao DataFrame
    rotas_cd1_local_a['Tempo Estimado de Viagem (Predito)'] = tempos_preditos

    # Ordenar pelas menores previsões
    rotas_cd1_local_a_ordenadas = rotas_cd1_local_a.sort_values(by='Tempo Estimado de Viagem (Predito)')

    # Selecionar as 3 melhores rotas
    melhores_rotas = rotas_cd1_local_a_ordenadas.head(3)

    # Reverter as colunas para os valores originais
    melhores_rotas['Destino da Entrega'] = label_encoders['Destino da Entrega'].inverse_transform(melhores_rotas['Destino da Entrega'])
    melhores_rotas['Condições de Tráfego'] = label_encoders['Condições de Tráfego'].inverse_transform(melhores_rotas['Condições de Tráfego'])
    melhores_rotas['Local de Partida'] = label_encoders['Local de Partida'].inverse_transform(melhores_rotas['Local de Partida'])

    # Exibir as 3 melhores rotas com colunas ajustadas
    result = (melhores_rotas[['Local de Partida', 'Destino da Entrega', 'Distância', 'Condições de Tráfego', 'Tempo Estimado de Viagem (Predito)']])
    
    return result

if __name__ == "__main__":
    local_partida = 'CD1'
    destino_entrega = 'Local A'
    encontrar_menor_tempo(local_partida, destino_entrega)