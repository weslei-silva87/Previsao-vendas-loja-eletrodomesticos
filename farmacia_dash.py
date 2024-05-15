import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from sklearn.linear_model import LinearRegression
import numpy as np

# Carregar os dados
tabela_nova = pd.read_csv('C:/Users/Weslei/Desktop/Projeto DS/tabela_farmacia.csv')

# Remover a coluna 'datum' se ela estiver presente
if 'datum' in tabela_nova.columns:
    tabela_nova.drop(columns=['datum'], inplace=True)

#====================================
# TITULO DO DASHBOARD
#===================================

# TITULO DO DASHBOARD
st.header('Dashboard Farmácia')

# Carregar a imagem
image_path = 'C:/Users/Weslei/Desktop/Projeto DS/logo farmarcia.png1.png'
image = Image.open(image_path)

# Exibir a imagem na barra lateral com largura específica
st.sidebar.image(image, width=120)

# Converter as colunas de medicamentos para tipo numérico
medicamentos = ['M01AB', 'M01AE', 'N02BA', 'N02BE', 'N05B', 'N05C', 'R03', 'R06']
tabela_nova[medicamentos] = tabela_nova[medicamentos].apply(pd.to_numeric, errors='coerce')

# CONSTRUINDO BARRA LATERAL
#===================================
st.sidebar.markdown('Filtros')
st.sidebar.markdown("""_____""")


# Adicionando um botão de atualização na barra lateral
btn_atualizar = st.sidebar.button("Atualizar")


# Obtendo os anos únicos da coluna "ano"
unique_years = tabela_nova['ano'].unique()

# Filtro de anos com checkboxes
selected_years = st.sidebar.multiselect(
    'Selecione o Ano',
    options=unique_years,
    default=unique_years,
)

# Filtro de meses com checkboxes
# Dicionário para mapear os números dos meses para os nomes dos meses
meses_map = {
    1: 'Janeiro',
    2: 'Fevereiro',
    3: 'Março',
    4: 'Abril',
    5: 'Maio',
    6: 'Junho',
    7: 'Julho',
    8: 'Agosto',
    9: 'Setembro',
    10: 'Outubro',
    11: 'Novembro',
    12: 'Dezembro'
}

# Obtendo os meses únicos da coluna "mes"
unique_months = sorted(tabela_nova['mes'].unique())

# Mapeando os números dos meses para os nomes dos meses
named_months = [meses_map[mes] for mes in unique_months]

# Filtro de meses com checkboxes
selected_months = st.sidebar.multiselect(
    'Selecione o Mês',
    options=unique_months,
    format_func=lambda x: named_months[unique_months.index(x)],  # Mapeando para o nome do mês
    default=unique_months,
)

# Filtrando os dados com base nos filtros selecionados
filtered_data = tabela_nova[tabela_nova['ano'].isin(selected_years) &
                            tabela_nova['mes'].isin(selected_months)]

# Verificar se o botão de atualização foi pressionado e atualizar os filtros
if btn_atualizar:
    filtered_data = tabela_nova[tabela_nova['ano'].isin(selected_years) &
                                tabela_nova['mes'].isin(selected_months)]

# Renderizando o conteúdo das abas selecionadas
selected_tab = st.radio("Selecione a aba desejada:", 
                        ["Painel Gerencial", "Previsão de Investimento"])

if selected_tab == "Painel Gerencial":
    st.title("Painel Gerencial")
    st.subheader("Quais medicamentos apresentaram aumento ou diminuição de demanda entre 2014 e 2019?")
    
    # Verificar se há dados disponíveis após os filtros serem aplicados
    if not filtered_data.empty and 'ano' in filtered_data.columns:
        # Calculando médias de demanda para diferentes medicamentos
        medias = {}
        for medicamento in filtered_data.columns[:-3]:  # Excluindo 'ano', 'mes' e 'Faturamento'
            medias[medicamento] = filtered_data.groupby('ano')[medicamento].mean()

        # Criando gráficos para cada medicamento em pares
        num_plots = len(medias)
        num_cols = 2
        num_rows = (num_plots + num_cols - 1) // num_cols

        fig, axs = plt.subplots(num_rows, num_cols, figsize=(10, 5*num_rows))
        axs = axs.ravel()

        for i, (medicamento, media) in enumerate(medias.items()):
            axs[i].plot(media.index, media.values, marker='o', linestyle='-')
            axs[i].set_title(f'Média de demanda para o medicamento {medicamento} por ano')
            axs[i].set_xlabel('Ano')
            axs[i].set_ylabel('Média de demanda')
            axs[i].set_facecolor('none')  # Definindo o fundo transparente

        # Ajustando o layout para evitar sobreposição de texto
        plt.tight_layout()

        # Exibindo o gráfico no Streamlit
        st.pyplot(fig)
    else:
        st.write("Nenhum dado disponível para os filtros selecionados.")
        
elif selected_tab == "Previsão de Investimento":
    st.title("Previsão de Investimento")
    st.subheader("Análise de Investimentos")
    st.write("Aqui está a análise de investimentos prevista para o próximo trimestre:")
    
    # Solicitar ao cliente os investimentos em porcentagem para cada classe de medicamento
    investimentos_percentuais = {}
    for classe in medicamentos:
        investimentos_percentuais[classe] = st.slider(f"Informe o investimento em porcentagem para a classe {classe}", min_value=0.0, max_value=100.0, step=0.1, value=0.0)

    # Exibir os valores dos investimentos inseridos pelo cliente
    st.write("Investimentos inseridos pelo cliente:")
    for classe, valor in investimentos_percentuais.items():
        st.write(f"{classe}: {valor}%")

    # Definir as colunas de interesse
    colunas_classes = ['M01AB', 'M01AE', 'N02BA', 'N02BE', 'N05B', 'N05C', 'R03', 'R06']

    # Somar as vendas mensais das diferentes classes para obter o faturamento total
    tabela_nova['faturamento'] = tabela_nova[colunas_classes].sum(axis=1)

    # Definir as colunas de recursos
    X = tabela_nova[colunas_classes]

    # Definir a variável alvo (faturamento)
    y = tabela_nova['faturamento']

    # Inicializar o modelo de regressão linear
    modelo_linear = LinearRegression()

    # Treinar o modelo de regressão linear
    modelo_linear.fit(X, y)

    # Converter os investimentos em valores absolutos
    vendas_atuais = tabela_nova[colunas_classes].mean()
    investimentos_absolutos = {}
    for classe, porcentagem in investimentos_percentuais.items():
        investimentos_absolutos[classe] = vendas_atuais[classe] * (1 + porcentagem / 100)

    # Fazer previsões de novas vendas com base nos investimentos absolutos
    faturamento_previsto = modelo_linear.predict([list(investimentos_absolutos.values())])

    # Arredondar o faturamento previsto para duas casas decimais
    faturamento_previsto = round(faturamento_previsto[0], 3)

    # Calculando o percentual de aumento ou queda nas vendas para cada medicamento
    percentuais = {}
    for classe, investimento_absoluto in investimentos_absolutos.items():
        percentual = (investimento_absoluto - vendas_atuais[classe]) / vendas_atuais[classe] * 100
        percentuais[classe] = round(percentual, 2)

    # Criando uma tabela para mostrar os resultados
    resultados = pd.DataFrame({
        'Medicamento': percentuais.keys(),
        'Percentual de Alteração nas Vendas (%)': percentuais.values(),
        'Vendas Atuais': vendas_atuais.values,
        'Projeção de Venda': [round(val, 2) for val in investimentos_absolutos.values()]
    })

    # Adicionando coluna com setas para indicar aumento ou queda nas vendas
    resultados['Seta'] = np.where(resultados['Percentual de Alteração nas Vendas (%)'] >= 0, '↑', '↓')

    # Calculando a porcentagem de alteração nos lucros
    resultados['Porcentagem de Alteração nos Lucros (%)'] = ((resultados['Projeção de Venda'] - resultados['Vendas Atuais']) / resultados['Vendas Atuais']) * 100

    # Excluindo a última coluna "Percentual de Alteração nas Vendas (%)"
    resultados = resultados.drop(columns=['Percentual de Alteração nas Vendas (%)'])

    # Exibindo a tabela com os resultados, incluindo a nova coluna
    st.write("Resultados:")
    st.dataframe(resultados.style.format({'Porcentagem de Alteração nos Lucros (%)': '{:.2f}%'}))

    # Realizando testes de R²
    r2 = modelo_linear.score(X, y)
    st.write(f"O coeficiente de determinação (R²) do modelo é: {r2:.2f}")

    # Mensagem para o cliente
    if r2 >= 0.8:
        st.success("O modelo de previsão possui uma boa capacidade de explicar a variação das vendas.")
    elif r2 >= 0.6:
        st.warning("O modelo de previsão possui uma capacidade moderada de explicar a variação das vendas.")
    else:
        st.error("O modelo de previsão possui uma capacidade baixa de explicar a variação das vendas.")




