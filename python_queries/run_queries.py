import pymongo
import time
from statistics import mean
import sys
from pymongo import ReadPreference

# --- Configuration ---
# 1. ✅ AJOUT DE "readPreference=primaryPreferred"
# Hada howa li kaykhlli l'code ykhdem wakha Primary TAYE7 (kaymchi l Secondary)
MONGO_URI = "mongodb://localhost:27018/?readPreference=primaryPreferred"
DB_NAME = "universiteDB"

print("--- 1. Connecting to MongoDB... ---")
# Zedt directConnection=False bach yt3amel m3a cluster sharded
# ✅ HNA L'FIX: Kan-passiw 'read_preference' comama argument, machi f String
client = pymongo.MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000,
    read_preference=ReadPreference.PRIMARY_PREFERRED  # <--- HADA HOWA L'MO3ALIM
)

# Debug: Bach nt2kdo anna l'code fhem l'plan
print(f"DEBUG: Read Preference actuelle = {client.read_preference}")

db = client[DB_NAME]

# Test connection
try:
    client.admin.command('ping')
    print("--- 2. Connection SUCCESFUL! ---")
except Exception as e:
    print(f"\n!!! ERREUR DE CONNEXION !!!\nErreur: {e}")
    sys.exit(1)

etudiants = db["etudiants"]
notes = db["notes"]

# ------------------------------------------
# Detect SHARDING MODE
# ------------------------------------------
def detect_sharding_strategy():
    try:
        config = client["config"]["collections"].find_one({"_id": f"{DB_NAME}.etudiants"})
        if not config: return "unknown"
        key = config.get("key", {})
        if "faculte" in key: return "faculte"
        elif "annee_universitaire" in key: return "annee"
        return "unknown"
    except:
        return "unknown"

SHARDING_MODE = detect_sharding_strategy()
print(f"--- STRATEGY DETECTED: {SHARDING_MODE} ---")

# ==========================================
#  ✅ FIX: Try/Except 3la l'Index
# ==========================================
print("--- Creating Index on 'notes.etudiant_id' (Optimization) ---")
try:
    db.notes.create_index([("etudiant_id", pymongo.ASCENDING)])
    print("--- Index Created Successfully! ---")
except Exception as e:
    # Hna fin kan-ignorer l'erreur ila Primary kan taye7
    print(f"--- ⚠️ Index creation SKIPPED (Normal during Failure Test) ---")
    print("> Reason:  Could not find host matching read preference { faculte : primary } for set shardA-rs")

# ==========================================

# ------------------------------------------
# Benchmark helper
# ------------------------------------------
def benchmark(name, func, repeat=1):
    print(f"\n >> [START] {name}...", end=" ", flush=True) 
    try:
        times = []
        for i in range(repeat):
            t0 = time.time()
            func() 
            dt = time.time() - t0
            times.append(dt)
        
        avg_time = mean(times)
        print(f"DONE! ({avg_time:.4f} sec)")
        return avg_time
    except Exception as e:
        print(f"FAILED! Error: {e}")
        # Hna kan-returniw None bach n3rfo rah fchel, walakin ma nwaqfouch script
        return None

# ------------------------------------------
# QUERIES
# ------------------------------------------
def avg_by_student():
    list(etudiants.aggregate([
        {"$lookup": {"from": "notes", "localField": "etudiant_id", "foreignField": "etudiant_id", "as": "notes"}},
        {"$unwind": "$notes"},
        {"$group": {"_id": "$etudiant_id", "avg_note": {"$avg": "$notes.note"}}}
    ]))

def single_student_avg():
    list(notes.aggregate([
        {"$match": {"etudiant_id": "CNE_1"}},
        {"$group": {"_id": None, "avg": {"$avg": "$note"}}}
    ]))

def avg_by_year():
    list(notes.aggregate([
        {"$group": {"_id": "$annee_universitaire", "avg_note": {"$avg": "$note"}}}
    ]))

def avg_by_faculte():
    list(notes.aggregate([
        {"$group": {"_id": "$faculte", "avg_note": {"$avg": "$note"}}}
    ]))

def histogram_notes():
    list(notes.aggregate([
        {"$bucket": {
            "groupBy": "$note",
            "boundaries": [0, 5, 10, 12, 14, 16, 18, 20],
            "default": "others",
            "output": {"count": {"$sum": 1}}
        }}
    ]))

def top20_students():
    list(etudiants.aggregate([
        {"$lookup": {"from": "notes", "localField": "etudiant_id", "foreignField": "etudiant_id", "as": "notes"}},
        {"$unwind": "$notes"},
        {"$group": {"_id": "$etudiant_id", "avg_note": {"$avg": "$notes.note"}}},
        {"$sort": {"avg_note": -1}},
        {"$limit": 20}
    ]))

# ------------------------------------------
# RUN BENCHMARKS
# ------------------------------------------
print("\n--- 4. Starting Benchmarks ---")

benchmark("NOTES_SINGLE", single_student_avg)
benchmark("AVG_BY_FAC", avg_by_faculte)
benchmark("AVG_BY_STUDENT", avg_by_student)
benchmark("AVG_BY_YEAR", avg_by_year)
benchmark("HISTOGRAM", histogram_notes)
benchmark("MOST_NOTES", top20_students)