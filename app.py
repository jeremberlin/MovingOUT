import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.set_page_config(page_title="Gantt Déménagements", layout="wide")
st.title("📊 Planning de Déménagements – Gantt interactif")

# 1) Charger le fichier depuis le repo (dans /data)
DATA_PATH = "data/gantt_python.xlsx"
df = pd.read_excel(DATA_PATH)

# 2) Nettoyage & renommage
df = df.rename(columns={
    'ID': 'task_id',
    'TÂCHE': 'description',
    'DÉBUT': 'Start',
    'FINI': 'Finish',
    'DEADLINE': 'Deadline',
    'Lié à': 'prédécesseurs',
    'AVANCEMENT': 'Progress'
})
df = df[[c for c in df.columns if c not in ('Unnamed: 2','nb jours')]]
df = df[df['task_id'].notna()].copy()

# 3) Préparation des données
df['description'] = df['description'].astype(str).apply(lambda x: re.sub(r'["\']','',x))
df['Start']  = pd.to_datetime(df['Start'],    dayfirst=True, errors='coerce')
df['Deadline']= pd.to_datetime(df['Deadline'],dayfirst=True, errors='coerce')
df['Finish'] = pd.to_datetime(df['Finish'],  dayfirst=True, errors='coerce').fillna(df['Deadline'])
df['prédécesseurs'] = df['prédécesseurs'].fillna('').astype(str)
df['Progress'] = pd.to_numeric(df['Progress'], errors='coerce').fillna(0).clip(0,100)

# 4) Sélecteur mode de vue
mode = st.sidebar.selectbox("Vue du Gantt", ["Day","Week","Month"])
# 5) Générer le Gantt via Plotly
fig = px.timeline(
    df,
    x_start="Start",
    x_end="Finish",
    y="description",
    color="Progress",
    color_continuous_scale="Blues",
    range_color=[0,100],
    title="Gantt – Avancement & dépendances"
)
fig.update_yaxes(autorange="reversed")
fig.update_layout(
    height=600,
    margin=dict(l=200, r=50, t=80, b=50),
    xaxis=dict(tickformat="%d-%m-%Y")
)
st.plotly_chart(fig, use_container_width=True)

# 6) Bouton de téléchargement PNG
if st.button("📥 Télécharger le Gantt en PNG"):
    fig.write_image("gantt_streamlit.png", scale=4)
    st.download_button("Télécharger", "gantt_streamlit.png", "image/png")

