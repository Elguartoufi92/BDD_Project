from fastapi import FastAPI, HTTPException
import pymongo
from pymongo import ReadPreference

app = FastAPI()

# ==============================================================================
# 1. CONFIGURATION MONGODB
# ==============================================================================
# Hna kan-sta3mlo Port 27018 (kima bddelti f docker-compose)
# options: serverSelectionTimeoutMS=2000 (Bach ma y-bloquich ila l-primary ta7)
MONGO_URI = "mongodb://localhost:27018,localhost:27019/?readPreference=primaryPreferred&serverSelectionTimeoutMS=2000"
DB_NAME = "universiteDB"

# Variable Globale l-Client
client = None
db = None
notes_col = None

try:
    print(f"📡 Connexion à MongoDB sur {MONGO_URI}...")
    client = pymongo.MongoClient(MONGO_URI)
    
    # Test Ping
    client.admin.command('ping')
    print("✅ Connexion API RÉUSSIE !")
    
    db = client[DB_NAME]
    
    # FORCE READ PREFERENCE SUR LA COLLECTION
    # Hada howa sirr bash l-failover ykhdem mzyan
    notes_col = db.get_collection("notes").with_options(read_preference=ReadPreference.PRIMARY_PREFERRED)

except Exception as e:
    print(f"❌ ERREUR CRITIQUE DE CONNEXION : {e}")

# ==============================================================================
# 2. ENDPOINTS (ROUTES)
# ==============================================================================

@app.get("/")
def home():
    """Health Check simple"""
    return {"status": "online", "system": "API Université Distribuée"}

@app.get("/shards-content")
def get_shards_content():
    """
    VERSION CORRIGÉE (UUID SUPPORT):
    Kybiyen chmen Facultés kinin f Shard A o chmen Facultés f Shard B.
    Kaysta3mel UUID bash ylqa les chunks f MongoDB 6.0+.
    """
    if not client:
        return {"success": False, "error": "Client not connected"}

    try:
        config_db = client["config"]
        
        # 1. ETAPE CRITIQUE: Njibu UUID dyal collection
        # Hada howa l-lien s7i7 bin Collection o Chunks f versions jdad
        coll_meta = config_db.collections.find_one({"_id": "universiteDB.etudiants"})
        
        if not coll_meta:
            return {
                "success": False, 
                "error": "Collection 'etudiants' non trouvée ou non shardée (Vérifiez setup_sharding)"
            }
            
        coll_uuid = coll_meta["uuid"] # <--- HADA HOWA L-MFT7

        # 2. Aggregation باستعمال UUID
        pipeline = [
            {"$match": {"uuid": coll_uuid}}, # <--- FIX: Kenna kandiro "ns", rddinaha "uuid"
            {"$group": {
                "_id": "$shard",
                "facultes": {
                    "$push": {
                        "min": "$min.faculte",
                        "max": "$max.faculte"
                    }
                }
            }}
        ]
        
        result = list(config_db.chunks.aggregate(pipeline))
        
        # 3. Formatting
        output = {}
        for item in result:
            shard_name = item["_id"]
            ranges = []
            for r in item["facultes"]:
                min_val = r.get("min", "MinKey")
                max_val = r.get("max", "MaxKey")
                
                # Nettoyage
                if isinstance(min_val, dict): min_val = "∞ (Début)"
                if isinstance(max_val, dict): max_val = "∞ (Fin)"
                
                ranges.append(f"{min_val} ➝ {max_val}")
            
            output[shard_name] = ranges

        return {
            "success": True,
            "data": output
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/cluster-full-stats")
def get_full_stats():
    """
    نسخة مطورة كتجيب الإحصائيات الحقيقية (Real Data Counts)
    """
    if not client:
        return {"success": False, "error": "Client not connected"}

    try:
        # 1. Shards Info
        config_db = client["config"]
        shards = list(config_db.shards.find({}, {"_id": 1, "host": 1, "state": 1}))
        
        # 2. Analyze 'etudiants' & 'notes'
        universite_db = client["universiteDB"]
        collections_stats = []
        
        target_colls = ["etudiants", "notes"]
        
        for col_name in target_colls:
            try:
                # A. Check Total Count
                total_docs = universite_db[col_name].count_documents({})
                
                # B. Distribution par Shard via $collStats
                # Hada howa l-mo3alim: Kayjib l-count mn kol shard
                pipeline = [{"$collStats": {"storageStats": {}}}]
                stats_cursor = universite_db[col_name].aggregate(pipeline)
                
                shard_breakdown = {}
                for stat in stats_cursor:
                    shard_name = stat["shard"]
                    count = stat["storageStats"]["count"]
                    size_mb = round(stat["storageStats"]["size"] / (1024*1024), 2)
                    
                    shard_breakdown[shard_name] = {
                        "count": count,
                        "size_mb": size_mb
                    }

                # C. Chunk Ranges (Bach n3rfo chmen Faculte fin jat)
                # Kanqraw mn config.chunks
                chunks_info = []
                ns = f"universiteDB.{col_name}"
                chunks = list(config_db.chunks.find({"ns": ns}))
                
                for c in chunks:
                    min_k = c.get("min", {}).get("faculte", "Min")
                    max_k = c.get("max", {}).get("faculte", "Max")
                    shard = c.get("shard")
                    chunks_info.append({
                        "shard": shard,
                        "range": f"[{min_k} ➝ {max_k}]"
                    })

                collections_stats.append({
                    "name": col_name,
                    "total": total_docs,
                    "breakdown": shard_breakdown, # Data Counts
                    "ranges": chunks_info         # Facultés Info
                })
                
            except Exception as e:
                print(f"Skipping {col_name}: {e}")

        return {
            "success": True,
            "shards": shards,
            "collections": collections_stats
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

# ==============================================================================
# Lancement (Optionnel si exécuté direct)
# ==============================================================================
if __name__ == "__main__":
    import uvicorn
    # Lanci l-server f port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)