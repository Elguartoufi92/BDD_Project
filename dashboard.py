import streamlit as st
import requests
import time
import pandas as pd

st.set_page_config(page_title="FINAL ARCHITECTURE", page_icon="🏛️", layout="wide")
st.title("🏛️ Architecture API + Frontend")
st.markdown("### Le test Ultime: Streamlit -> FastAPI -> MongoDB Sharded")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Connexion API")
    api_url = st.text_input("URL API", "http://127.0.0.1:8000")
    
    if st.button("Ping API"):
        try:
            res = requests.get(f"{api_url}/")
            if res.status_code == 200:
                st.success("✅ API En Ligne")
            else:
                st.error("⚠️ API Erreur")
        except:
            st.error("❌ API Éteinte")

# --- LE TEST ---
st.divider()
st.subheader("⚡ Test de Lecture (Fault Tolerance)")

st.info("ℹ️ Ce bouton envoie une requête HTTP à l'API. L'API va chercher la donnée dans MongoDB (Replica).")

if st.button("▶️ DEMANDER LA NOTE À L'API", type="primary", use_container_width=True):
    status = st.empty()
    status.info("⏳ Envoi de la requête à l'API...")
    
    start = time.time()
    try:
        # L'APPEL API (Machi Mongo Direct)
        response = requests.get(f"{api_url}/read-note")
        data = response.json()
        dur = time.time() - start
        
        if data.get("success"):
            status.success(f"✅ SUCCÈS ! (Réponse reçue en {dur:.4f}s)")
            st.metric("Moyenne (Via API)", f"{data['avg']:.2f}")
            st.balloons()
        else:
            status.error(f"❌ ÉCHEC API: {data.get('error')}")
            
    except Exception as e:
        status.error(f"❌ Impossible de joindre l'API: {e}")