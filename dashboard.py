import streamlit as st
import requests
import time
import pandas as pd
import plotly.express as px 

# 1. PAGE CONFIG
st.set_page_config(page_title="FINAL ARCHITECTURE", page_icon="🏛️", layout="wide")
st.title("🏛️ Dashboard: Université Distribuée")
st.markdown("### Control Center: FastAPI + MongoDB Sharded Cluster")

# 2. SIDEBAR (CONNEXION)
with st.sidebar:
    st.header("🔌 Connexion API")
    api_url = st.text_input("URL API", "http://127.0.0.1:8000")
    
    st.divider()
    
    if st.button("Ping API"):
        try:
            res = requests.get(f"{api_url}/")
            if res.status_code == 200:
                st.success("✅ API En Ligne")
            else:
                st.error("⚠️ API Erreur")
        except:
            st.error("❌ API Éteinte")

# 3. DEFINITION DES TABS (Hna fin kankhelo Tab 1 o Tab 2 ybano)
tab1, tab2 = st.tabs(["🔥 Chaos Test (Lecture)", "📊 État du Cluster (Data)"])

# ==============================================================================
# TAB 1: TEST DE LECTURE (CHAOS)
# ==============================================================================
# ==============================================================================
# TAB 1: TEST DE LECTURE (CHAOS) - VERSION CORRIGÉE
# ==============================================================================
with tab1:
    st.subheader("⚡ Test de Lecture (Fault Tolerance)")
    st.info("ℹ️ Ce test vérifie si l'API peut lire les données même si le Primary est en panne.")

    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.button("▶️ DEMANDER LA NOTE", type="primary", use_container_width=True):
            status = st.empty()
            status.info("⏳ Requête envoyée...")
            
            start = time.time()
            try:
                # Appel API
                response = requests.get(f"{api_url}/read-note", timeout=5) # Zedt timeout 5s
                dur = time.time() - start
                
                # --- HNA FIN KAN-FIXIW L-ERROR ---
                if response.status_code == 200:
                    try:
                        data = response.json() # 3ad kan-7awlo nqraw JSON
                        if data.get("success"):
                            status.success(f"✅ SUCCÈS ({dur:.4f}s)")
                            st.metric("Moyenne reçue", f"{data['avg']:.2f} / 20")
                            if data.get("source"):
                                st.caption(f"Source: {data['source']}")
                        else:
                            status.error(f"❌ ÉCHEC LOGIQUE: {data.get('error')}")
                    except ValueError:
                        # Ila rje3 HTML wla Text (Machi JSON)
                        status.error(f"❌ ERREUR FORMAT: L'API n'a pas renvoyé de JSON. (Status: {response.status_code})")
                        with st.expander("Voir la réponse brute"):
                            st.text(response.text)
                else:
                    # Ila l-API rje3 500 Internal Server Error
                    status.error(f"❌ ERREUR SERVEUR ({response.status_code})")
                    with st.expander("Détails"):
                        st.text(response.text)
                    
            except requests.exceptions.ConnectionError:
                status.error("❌ Impossible de contacter l'API (Connection Refused)")
            except Exception as e:
                status.error(f"❌ Erreur Inattendue: {e}")

# ==============================================================================
# TAB 2: DATA & SHARDING INTELLIGENCE (STATS)
# ==============================================================================
with tab2:
    st.subheader("📊 Répartition Réelle des Données")
    
    if st.button("🔄 Actualiser les stats", use_container_width=True):
        with st.spinner("Analyse du cluster en cours..."):
            try:
                response = requests.get(f"{api_url}/cluster-full-stats")
                data = response.json()
                
                if data.get("success"):
                    colls = data.get("collections", [])
                    
                    if not colls:
                        st.warning("⚠️ Aucune donnée trouvée. (Avez-vous lancé setup_sharding ?)")
                    
                    for col in colls:
                        st.divider()
                        st.markdown(f"### 📂 Collection: `{col['name']}`")
                        
                        # 1. Total Metrics
                        total = col['total']
                        st.metric("Total Documents", f"{total:,}", delta="Global")
                        
                        # 2. Shard Breakdown (Les colonnes)
                        breakdown = col['breakdown']
                        ranges = col['ranges']
                        
                        c1, c2 = st.columns(2)
                        
                        # --- SHARD A ---
                        stats_a = breakdown.get("shardA-rs", {"count": 0})
                        range_a = [r['range'] for r in ranges if r['shard'] == 'shardA-rs']
                        
                        with c1:
                            st.info(f"🔹 **Shard A** (Primary)")
                            st.write(f"**Nombre:** `{stats_a['count']:,}` docs")
                            if total > 0:
                                perc_a = (stats_a['count'] / total) * 100
                                st.progress(perc_a / 100, text=f"{perc_a:.1f}% des données")
                            
                            if range_a:
                                st.markdown("**🗂️ Facultés hébergées :**")
                                for r in range_a:
                                    st.code(r, language="text")

                        # --- SHARD B ---
                        stats_b = breakdown.get("shardB-rs", {"count": 0})
                        range_b = [r['range'] for r in ranges if r['shard'] == 'shardB-rs']
                        
                        with c2:
                            st.info(f"🔸 **Shard B**")
                            st.write(f"**Nombre:** `{stats_b['count']:,}` docs")
                            if total > 0:
                                perc_b = (stats_b['count'] / total) * 100
                                st.progress(perc_b / 100, text=f"{perc_b:.1f}% des données")
                                
                            if range_b:
                                st.markdown("**🗂️ Facultés hébergées :**")
                                for r in range_b:
                                    st.code(r, language="text")
                                    
                        # 3. Visualisation Graphique (Plotly)
                        if total > 0:
                            st.write("#### 📈 Visualisation de l'Équilibre")
                            chart_data = [
                                {"Shard": "Shard A", "Documents": stats_a['count']},
                                {"Shard": "Shard B", "Documents": stats_b['count']}
                            ]
                            fig = px.bar(
                                chart_data, 
                                x="Shard", 
                                y="Documents", 
                                color="Shard", 
                                text="Documents",
                                color_discrete_sequence=["#3b8ed0", "#e0a32e"] # Bleu et Orange
                            )
                            st.plotly_chart(fig, use_container_width=True)

                else:
                    st.error(f"Erreur API: {data.get('error')}")

            except Exception as e:
                st.error(f"Erreur Connexion: {e}")