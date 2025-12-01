from fastapi import FastAPI, HTTPException
import pymongo
from pymongo import ReadPreference

app = FastAPI()

# --- CONFIGURATION MONGODB ---
# Hna fin kan-l3bo b l'options d l'connexion
MONGO_URI = "mongodb://localhost:27018/?readPreference=primaryPreferred&serverSelectionTimeoutMS=2000"
DB_NAME = "universiteDB"

# Connexion Global (Bach tbqa 7yya dima)
try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    # Collection 'notes' mregla 3la Replica bzaz
    notes_col = db.get_collection("notes", read_preference=ReadPreference.PRIMARY_PREFERRED)
    print("✅ API Connectée à MongoDB (Mode Replica Ready)")
except Exception as e:
    print(f"❌ Erreur Connexion: {e}")

@app.get("/")
def home():
    return {"status": "API En Ligne", "message": "Fault Tolerance Backend"}

@app.get("/read-note")
def read_note():
    """Hadi hiya l'fonction li ghat-testi l'Fault Tolerance"""
    try:
        # Requete simple
        result = list(notes_col.aggregate([
            {"$match": {"etudiant_id": "CNE_1"}},
            {"$group": {"_id": None, "avg": {"$avg": "$note"}}}
        ]))
        
        if result:
            return {"success": True, "avg": result[0]['avg'], "source": "Replica ou Primary"}
        else:
            return {"success": False, "message": "Aucune donnée trouvée"}
            
    except Exception as e:
        # Hna kan-returniw l'erreur l l'Frontend
        return {"success": False, "error": str(e)}

@app.get("/check-docker")
def check_status():
    """Check simple pour voir si l'API repond"""
    return {"status": "ok"}
