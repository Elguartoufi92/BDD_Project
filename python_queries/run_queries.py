import pymongo
import time
import sys
from statistics import mean
from pymongo import ReadPreference

# =============================================================================
# SCRIPT DE BENCHMARK & CHAOS TEST - FINAL FIX
# =============================================================================

# 1. DETECTION DU MODE (via Arguments)
# -----------------------------------------------------------------------------
IS_CHAOS_MODE = "--chaos" in sys.argv

print(f"\n{'='*60}")
if IS_CHAOS_MODE:
    print("🔥 MODE CHAOS DETECTÉ (Lecture Seule / Tolérance Panne) 🔥")
    print("   -> Strategie: ReadPreference.PRIMARY_PREFERRED")
    print("   -> Action: Creation Index DESACTIVÉE (Write unsafe)")
    
    # ✅ FIX 1: URI Options pour Chaos
    URI_OPTIONS = "?readPreference=primaryPreferred"
    MY_READ_PREF = ReadPreference.PRIMARY_PREFERRED
else:
    print("✅ MODE NORMAL (Performance Standard) ✅")
    print("   -> Strategie: ReadPreference.PRIMARY")
    print("   -> Action: Creation Index ACTIVÉE")
    
    URI_OPTIONS = ""
    MY_READ_PREF = ReadPreference.PRIMARY
print(f"{'='*60}\n")


print("--- 1. Connecting to MongoDB... ---")

# ✅ FIX 2: Port 27017 (Interne Docker) + Dynamic Options
MONGO_URI = f"mongodb://localhost:27017/{URI_OPTIONS}"
DB_NAME = "universiteDB"

client = pymongo.MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000,
    read_preference=MY_READ_PREF
)

# Debug
print(f"DEBUG: Read Preference actuelle = {client.read_preference}")

db = client[DB_NAME]

# Test connection
try:
    client.admin.command('ping')
    print("--- 2. Connection SUCCESFUL! ---")
except Exception as e:
    print(f"\n!!! ERREUR DE CONNEXION !!!\nErreur: {e}")
    sys.exit(1)

# 🛑 FIX 3: FORCER LE READ PREFERENCE SUR LES COLLECTIONS 🛑
# Hada howa l-ferq l-kbir: Kanbzzo 3la collection tqra mn Secondary
if IS_CHAOS_MODE:
    print("--- ⚙️  Application du ReadPreference sur les Collections... ---")
    etudiants = db.get_collection("etudiants").with_options(read_preference=ReadPreference.PRIMARY_PREFERRED)
    notes = db.get_collection("notes").with_options(read_preference=ReadPreference.PRIMARY_PREFERRED)
else:
    etudiants = db["etudiants"]
    notes = db["notes"]



# Detect SHARDING MODE (Via Indexes) - FIX
# ------------------------------------------
def detect_sharding_strategy():
    try:
        config = client["config"]["collections"].find_one({"_id": f"{DB_NAME}.etudiants"})
        if not config:
            return "unknown"

        key = config.get("key", {})
        if "faculte" in key:
            return "faculte"
        elif "annee_universitaire" in key:
            return "annee"
        return "unknown"
    except:
        return "unknown"

SHARDING_MODE = detect_sharding_strategy()
print(f"--- DETECTED STRATEGY: {SHARDING_MODE} ---")

# 3. OPTIMISATION (INDEX) - VERSION INTELLIGENTE
# -----------------------------------------------------------------------------
if not IS_CHAOS_MODE:
    print("\n--- [NORMAL] Vérification de l'Index sur 'etudiant_id' ---")
    try:
        # 1. Kan-jebdo les indexes li kaynin db
        existing_indexes = db.notes.index_information()
        
        # 2. Kan-checkiw wach "etudiant_id_1" kayn (Smia par défaut dyal mongo)
        if "etudiant_id_1" in existing_indexes:
            print("ℹ️  [INFO] Index déjà présent. SKIP.")
        else:
            # 3. Ila ma kanch, 3ad kan-creeriweh
            print("⏳ Création de l'index en cours...")
            db.notes.create_index([("etudiant_id", pymongo.ASCENDING)])
            print("✅ Index créé avec succès.")
            
    except Exception as e:
        print(f"⚠️ Erreur création index: {e}")
else:
    print("\n--- [CHAOS] ⏩ Index Creation SKIPPED (Sécurité: Write operation unsafe) ---")

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
        return None

# ------------------------------------------
# QUERIES
# ------------------------------------------
def avg_by_student():
    # METHODE OPTIMISEE (Sans $lookup)
    # Kan-sta3mlo l-Index 'etudiant_id' li saybna direct f notes
    list(notes.aggregate([
        # 1. Group by etudiant_id (Local Index Usage)
        {"$group": {
            "_id": "$etudiant_id", 
            "avg_note": {"$avg": "$note"}
        }},
        # 2. Limit (Bach ma y-explozich l-RAM ila kano millions)
        {"$limit": 100} 
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
    # METHODE OPTIMISEE (Sans $lookup)
    # Kan-khdmo direct 3la collection 'notes'
    try:
        list(notes.aggregate([
            # 1. Group par étudiant bash n7sbo l-moyenne
            {"$group": {
                "_id": "$etudiant_id", 
                "avg_note": {"$avg": "$note"}
            }},
            # 2. Sort decroissant (mn l-kbir l-sghir)
            {"$sort": {"avg_note": -1}},
            # 3. Limit (Top 20)
            {"$limit": 20}
        ]))
    except Exception as e:
        print(f" (Info: Lookup complex failed in Chaos: {e})", end="")

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