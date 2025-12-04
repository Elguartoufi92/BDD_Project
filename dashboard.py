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
# TAB 1: LOCALISATION DES DONNÉES (QUI EST OÙ ?)
# ==============================================================================
with tab1:
    st.subheader("🗺️ Cartographie des Données")
    st.info("ℹ️ Ce test interroge le Routeur pour savoir quelles Facultés sont stockées sur quel Shard.")

    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("📍 VOIR LA RÉPARTITION", type="primary", use_container_width=True):
            status = st.empty()
            
            try:
                # Appel au nouvel endpoint
                response = requests.get(f"{api_url}/shards-content")
                data = response.json()
                
                if data.get("success"):
                    status.success("Données récupérées !")
                    content = data.get("data", {})
                    
                    # Affichage Joli (Cards)
                    c_a, c_b = st.columns(2)
                    
                    with c_a:
                        st.markdown("### 🟦 Shard A (Primary)")
                        ranges_a = content.get("shardA-rs", [])
                        if ranges_a:
                            for r in ranges_a:
                                st.info(f"🏫 {r}")
                        else:
                            st.caption("Aucune donnée assignée.")

                    with c_b:
                        st.markdown("### 🟧 Shard B")
                        ranges_b = content.get("shardB-rs", [])
                        if ranges_b:
                            for r in ranges_b:
                                st.warning(f"🏫 {r}")
                        else:
                            st.caption("Aucune donnée assignée.")
                            
                else:
                    status.error(f"❌ Erreur: {data.get('error')}")
                    
            except Exception as e:
                status.error(f"❌ Impossible de joindre l'API: {e}")

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