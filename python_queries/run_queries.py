import pymongo
import time
from statistics import mean
from pymongo import MongoClient

# --- Configuration ---
MONGO_URI = "mongodb://localhost:27018/"
DB_NAME = "universiteDB"

client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]

etudiants = db["etudiants"]
notes = db["notes"]

# ------------------------------------------
# Detect SHARDING MODE (FACULTE vs ANNEE)
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

# ------------------------------------------
# Benchmark helper (MODIFIED FOR VISUAL OUTPUT)
# ------------------------------------------
def benchmark(name, func, repeat=1):  # <--- Changed repeat to 1 for speed
    print(f" >> Running: {name}...", end=" ", flush=True) # Prints immediately
    
    times = []
    for _ in range(repeat):
        t0 = time.time()
        func()
        times.append(time.time() - t0)
    
    avg_time = mean(times)
    print(f"Done! ({avg_time:.4f} sec)")
    return avg_time

# ------------------------------------------
# 6 QUERIES TO TEST
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
# RUN BENCHMARKS (Updated with Names)
# ------------------------------------------

# We pass a name now so we can see it in the terminal
results = {
    "AVG_BY_STUDENT": benchmark("AVG_BY_STUDENT", avg_by_student),
    "NOTES_SINGLE":   benchmark("NOTES_SINGLE", single_student_avg),
    "AVG_BY_YEAR":    benchmark("AVG_BY_YEAR", avg_by_year),
    "AVG_BY_FAC":     benchmark("AVG_BY_FAC", avg_by_faculte),
    "HISTOGRAM":      benchmark("HISTOGRAM", histogram_notes),
    "MOST_NOTES":     benchmark("MOST_NOTES", top20_students)
}

# ------------------------------------------
# WRITE RESULTS TO FILE
# ------------------------------------------

filename = "results_unknown.txt"

if SHARDING_MODE == "faculte":
    filename = "results_faculte.txt"
elif SHARDING_MODE == "annee":
    filename = "results_annee.txt"

with open(filename, "w") as f:
    f.write(f"===========(sharding_by_{SHARDING_MODE}) ===========\n\n")
    for key, val in results.items():
        f.write(f"{key}: {val:.4f} sec\n")
    f.write("\n================================\n")

print(f"\n--- Success! Results saved in: {filename} ---")