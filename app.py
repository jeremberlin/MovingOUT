import streamlit as st
import pandas as pd
import re, json
import streamlit.components.v1 as components

st.set_page_config(page_title="Gantt Déménagements", layout="wide")
st.title("📊 Planning de Déménagements – Gantt interactif")

# 1) Charger le fichier Excel
DATA_PATH = "data/gantt_python.xlsx"
df = pd.read_excel(DATA_PATH)

# 2) Nettoyage & renommage EXACTEMENT comme avant...
df = df.rename(columns={
    'ID':'id','TÂCHE':'name','DÉBUT':'start','FINI':'end',
    'DEADLINE':'deadline','Lié à':'dependencies','AVANCEMENT':'progress'
})
df = df[[c for c in df.columns if c not in ('Unnamed: 2','nb jours')]]
df = df[df['id'].notna()].copy()
df['id'] = df['id'].astype(int).astype(str)
df['name'] = df['name'].astype(str).apply(lambda x: re.sub(r'["\']','',x))
df['start'] = pd.to_datetime(df['start'], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')
df['deadline'] = pd.to_datetime(df['deadline'], dayfirst=True, errors='coerce')
df['end'] = pd.to_datetime(df['end'], dayfirst=True, errors='coerce')\
             .dt.strftime('%Y-%m-%d').fillna(df['deadline'].dt.strftime('%Y-%m-%d'))
df['dependencies'] = df['dependencies'].fillna('').astype(str).str.replace(' ', '')
df['progress'] = pd.to_numeric(df['progress'], errors='coerce').fillna(0).clip(0,100).astype(int)

# 3) Créer la liste de tâches JSON pour Frappe Gantt
tasks = df[['id','name','start','end','progress','dependencies']].to_dict(orient='records')
tasks_json = json.dumps(tasks)

# 4) Générer le mini-HTML à embarquer
gantt_html = f"""
<link rel="stylesheet" href="https://unpkg.com/frappe-gantt/dist/frappe-gantt.css" />
<div id="gantt"></div>
<script src="https://unpkg.com/frappe-gantt/dist/frappe-gantt.min.js"></script>
<script>
  document.addEventListener('DOMContentLoaded', function() {{
    const tasks = {tasks_json};
    const gantt = new Gantt("#gantt", tasks, {{
      view_mode: "Day",
      date_format: "YYYY-MM-DD",
      custom_popup_html: task => `
        <div class="details-container">
          <h5>${{task.name}}</h5>
          <p><strong>Start:</strong> ${{task.start}}</p>
          <p><strong>End:</strong> ${{task.end}}</p>
          <p><strong>Progress:</strong> ${{task.progress}}%</p>
        </div>`
    }});
  }});
</script>
<style>
  /* Assure que le gantt occupe tout l'espace */
  #gantt {{ height: 700px; width: 100%; }}
  body {{ margin:0; padding:0; }}
</style>
"""

# 5) Afficher dans Streamlit
components.html(gantt_html, height=750, scrolling=True)
