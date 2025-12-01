import pymongo
import time
import sys
from statistics import mean
from pymongo import ReadPreference

# =============================================================================
# SCRIPT DE BENCHMARK & CHAOS TEST - VERSION CORRIGÉE
# =============================================================================

# 1. DETECTION DU MODE (via Arguments)
IS_CHAOS_MODE = "--chaos" in sys.argv

print(f"\n{'='*60}")
if IS_CHAOS_MODE:
    print("🔥 MODE CHAOS DETECTÉ (Lecture Seule / Tolérance Panne) 🔥")
    print("   -> Strategie: ReadPreference.PRIMARY_PREFERRED")
    print("   -> Action: Creation Index DESACTIVÉE")
    
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

# Configuration Docker Interne
MONGO_URI = f"mongodb://localhost:27017/{URI_OPTIONS}"
DB_NAME = "universiteDB"

client = pymongo.MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000,
    read_preference=MY_READ_PREF
)

print(f"DEBUG: Read Preference actuelle = {client.read_preference}")

db = client[DB_NAME]

# Test connection
try:
    client.admin.command('ping')
    print("--- 2. Connection SUCCESFUL! ---")
except Exception as e:
    print(f"\n!!! ERREUR DE CONNEXION !!!\nErreur: {e}")
    sys.exit(1)

# FORCER LE READ PREFERENCE
if IS_CHAOS_MODE:
    print("--- ⚙️  Application du ReadPreference sur les Collections... ---")
    etudiants = db.get_collection("etudiants").with_options(read_preference=ReadPreference.PRIMARY_PREFERRED)
    notes = db.get_collection("notes").with_options(read_preference=ReadPreference.PRIMARY_PREFERRED)
else:
    etudiants = db["etudiants"]
    notes = db["notes"]


# =============================================================================
# 🛑 FIX: DETECTION DU SHARDING (INTEGRÉE ICI)
# =============================================================================
def detect_sharding_strategy():
    print("DEBUG: Analyse des Indexes...", end=" ")
    try:
        # Kan-qellbo 3la l-indexes f collection 'etudiants'
        indexes = etudiants.index_information()
        
        if "faculte_1" in indexes:
            return "faculte"
        elif "annee_universitaire_1" in indexes:
            return "annee"
        else:
            # Fallback: Config DB
            config_doc = client["config"]["collections"].find_one({"_id": f"{DB_NAME}.etudiants"})
            if config_doc:
                key = config_doc.get("key", {})
                if "faculte" in key: return "faculte"
                if "annee_universitaire" in key: return "annee"
            return "unknown"
            
    except Exception as e:
        print(f"(Warning: {e})", end=" ")
        return "unknown"

SHARDING_MODE = detect_sharding_strategy()
print(f"--- DETECTED STRATEGY: {SHARDING_MODE} ---")


# =============================================================================
# 3. OPTIMISATION (INDEX)
# =============================================================================
if not IS_CHAOS_MODE:
    print("\n--- [NORMAL] Création de l'Index sur 'etudiant_id' ---")
    try:
        db.notes.create_index([("etudiant_id", pymongo.ASCENDING)])
        print("✅ Index créé avec succès.")
    except Exception as e:
        print(f"⚠️ Erreur création index: {e}")
else:
    print("\n--- [CHAOS] ⏩ Index Creation SKIPPED (Write operation unsafe) ---")


# =============================================================================
# 4. BENCHMARK HELPER
# =============================================================================
def benchmark(name, func, repeat=1):
    print(f" >> [START] {name}...", end=" ", flush=True) 
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

# =============================================================================
# 5. REQUETES (QUERIES) - OPTIMISÉES
# =============================================================================

def single_student_avg():
    # Simple read
    list(notes.aggregate([
        {"$match": {"etudiant_id": "CNE_1"}},
        {"$group": {"_id": None, "avg": {"$avg": "$note"}}}
    ]))

def avg_by_faculte():
    # Sharding Key
    list(notes.aggregate([
        {"$group": {"_id": "$faculte", "avg_note": {"$avg": "$note"}}}
    ]))

def avg_by_year():
    # Scatter-Gather (Global)
    list(notes.aggregate([
        {"$group": {"_id": "$annee_universitaire", "avg_note": {"$avg": "$note"}}}
    ]))

def avg_by_student():
    # ✅ OPTIMISÉE: Plus de $lookup, direct sur notes
    list(notes.aggregate([
        {"$group": {
            "_id": "$etudiant_id", 
            "avg_note": {"$avg": "$note"}
        }},
        {"$limit": 100} 
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
    # ✅ OPTIMISÉE: Plus de $lookup, direct sur notes
    try:
        list(notes.aggregate([
            {"$group": {
                "_id": "$etudiant_id", 
                "avg_note": {"$avg": "$note"}
            }},
            {"$sort": {"avg_note": -1}},
            {"$limit": 20}
        ]))
    except Exception as e:
        print(f" (Error: {e})", end="")

# ------------------------------------------
# RUN BENCHMARKS
# ------------------------------------------
print("\n--- 4. Starting Benchmarks ---")

benchmark("NOTES_SINGLE", single_student_avg)
benchmark("AVG_BY_FAC", avg_by_faculte)
benchmark("AVG_BY_STUDENT", avg_by_student)
benchmark("AVG_BY_YEAR", avg_by_year)
benchmark("HISTOGRAM", histogram_notes)
benchmark("MOST_NOTES (TOP 20)", top20_students)

print("\n✅ Terminé.")