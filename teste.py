import streamlit as st
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine, text

# Configuração da conexão com o banco de dados
DATABASE_URL = "postgresql+psycopg2://dry_eye_project_user:08g6Y8atMBzDp4IB8f5maqeFVI7lwUHy@dpg-cv7o2iij1k6c739ggh60-a.oregon-postgres.render.com:5432/dry_eye_test"
engine = create_engine(DATABASE_URL)

# Criar view para armazenar dados processados
view_query = text("""
    CREATE OR REPLACE VIEW chance_doenca_view AS
    SELECT p.nome, p.genero, q.chance_doenca, q.fadiga_ocular, q.vermelhidao_ocular, 
           q.irritacao_ocular, q.tempo_medio_tela, q.qualidade_sono
    FROM participante p
    JOIN questionario q ON p.id_participante = q.id_participante_id;
""")

st.title("Dry Eye Discover")
st.write("Este aplicativo apresenta análises sobre a doença do olho seco.")

# --- Gráfico 1: Distribuição da Chance da Doença ---
query_chance = """
    SELECT nome, chance_doenca FROM chance_doenca_view;
"""
df_chance = pd.read_sql_query(query_chance, engine)
df_chance['faixa_chance'] = pd.cut(df_chance['chance_doenca'], 
                                   bins=[0, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                                   labels=['0-50%', '51-60%', '61-70%', '71-80%', '81-90%', '91-100%'])
df_chance_grouped = df_chance.groupby('faixa_chance', observed=False).size().reset_index(name='quantidade')
fig_chance = px.bar(df_chance_grouped, x='faixa_chance', y='quantidade',
                    title='Quantidade de Participantes por Faixa de Chance da Doença',
                    labels={'faixa_chance': 'Faixa de Chance (%)', 'quantidade': 'Número de Participantes'},
                    color='faixa_chance')
st.plotly_chart(fig_chance)

# --- Gráfico 2: Proporção de Sintomas Oculares ---
query_sintomas = """
    SELECT SUM(fadiga_ocular::int) AS fadiga, 
           SUM(vermelhidao_ocular::int) AS vermelhidao, 
           SUM(irritacao_ocular::int) AS irritacao 
    FROM chance_doenca_view;
"""
df_sintomas = pd.read_sql_query(query_sintomas, engine)
fig_sintomas = px.pie(names=['Fadiga Ocular', 'Vermelhidão Ocular', 'Irritação Ocular'],
                      values=df_sintomas.iloc[0],
                      title='Proporção de Participantes com Sintomas Oculares')
st.plotly_chart(fig_sintomas)

# --- Gráfico 3: Relação entre Tempo de Tela e Chance da Doença ---
query_tela_doenca = """
    SELECT nome, tempo_medio_tela, chance_doenca FROM chance_doenca_view;
"""
df_tela_doenca = pd.read_sql_query(query_tela_doenca, engine)
fig_tela_doenca = px.bar(df_tela_doenca, x='tempo_medio_tela', y='chance_doenca',
                         title='Relação entre Tempo de Tela e Chance da Doença',
                         color='nome')
st.plotly_chart(fig_tela_doenca)

# --- Gráfico 4: Média de Qualidade do Sono por Gênero ---
query_sono = """
    SELECT genero, AVG(qualidade_sono) AS media 
    FROM chance_doenca_view
    GROUP BY genero;     
"""
df_sono = pd.read_sql_query(query_sono, engine)
fig_sono = px.bar(df_sono, x='genero', y='media', title='Média de Qualidade de Sono por Gênero',
                  labels={'genero': 'Gênero', 'media': 'Média da Qualidade do Sono'},
                  color='genero')
st.plotly_chart(fig_sono)


query_estresse = """
    SELECT tempo_medio_tela, AVG(chance_doenca) AS media_chance
    FROM chance_doenca_view
    GROUP BY tempo_medio_tela
    ORDER BY tempo_medio_tela;
"""
df_estresse = pd.read_sql_query(query_estresse, engine)
fig_estresse = px.line(df_estresse, x='tempo_medio_tela', y='media_chance',
                       title='Relação entre Nível de Estresse e Chance da Doença',
                       labels={'tempo_medio_tela': 'Tempo Médio de Tela', 'media_chance': 'Média da Chance (%)'},
                       markers=True)
st.plotly_chart(fig_estresse)