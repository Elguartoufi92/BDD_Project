import pymongo
from faker import Faker
import random
import time

# --- Configuration ---
# Connexion au routeur Mongos (et non directement à un Shard)
MONGO_URI = "mongodb://localhost:27018/"  # [cite: 171]
DB_NAME = "universiteDB"                  # [cite: 172]
NUM_ETUDIANTS = 50000                  # 1 Million d'étudiants [cite: 173]
NUM_NOTES_PER_ETUDIANT = 5                # 5 notes par étudiant [cite: 174]
BATCH_SIZE = 500                        # Insertion par lots de 10k pour la performance [cite: 175]

# --- Données de référence ---
fake = Faker('fr_FR')                     # [cite: 177]
facultes = ["Faculte A", "Faculte B", "Faculte C", "Faculte D"] # [cite: 178]
annees = ["2022-2023", "2023-2024", "2024-2025"]                # [cite: 179]
modules = ["Module_1", "Module_2", "Module_3", "Module_4", "Module_5"] # [cite: 182]

# --- Connexion ---
client = pymongo.MongoClient(MONGO_URI)   # [cite: 184]
db = client[DB_NAME]                      # [cite: 185]
etudiants_col = db["etudiants"]           # [cite: 186]
notes_col = db["notes"]                   # [cite: 187]

# --- Génération ---
print(f"Debut de la generation de {NUM_ETUDIANTS} etudiants...")
start_time = time.time()                  # [cite: 191]

etudiants_batch = []
notes_batch = []

for i in range(NUM_ETUDIANTS):            # [cite: 195]
    
    # --- DÉNORMALISATION (CRITIQUE POUR LE SHARDING) ---
    # On choisit la Faculté et l'Année UNE SEULE FOIS pour l'étudiant
    # et on va copier ces valeurs partout (dans l'étudiant et ses notes).
    fac = random.choice(facultes)         # [cite: 199]
    annee = random.choice(annees)         # [cite: 200]

    # 1. Création de l'étudiant
    etudiant = {
        "etudiant_id": f"CNE_{i+1}",      # [cite: 205]
        "nom": fake.last_name(),          # [cite: 207]
        "prenom": fake.first_name(),      # [cite: 209]
        "faculte": fac,                   # <--- Copié ici (Shard Key potentielle) [cite: 240]
        "annee_universitaire": annee      # <--- Copié ici (Shard Key potentielle) [cite: 241]
    }
    etudiants_batch.append(etudiant)      # [cite: 242]

    # 2. Génération des notes pour cet étudiant
    for j in range(NUM_NOTES_PER_ETUDIANT): # [cite: 244]
        note = {
            "etudiant_id": f"CNE_{i+1}",  # Lien vers l'étudiant [cite: 246]
            "module": random.choice(modules), # [cite: 247]
            "note": round(random.uniform(5.5, 19.5), 2), # [cite: 248]
            "faculte": fac,               # <--- DÉNORMALISATION: On répète la faculté [cite: 249]
            "annee_universitaire": annee  # <--- DÉNORMALISATION: On répète l'année [cite: 257]
        }
        notes_batch.append(note)          # [cite: 250]

    # --- Insertion par Lots (Batch Insert) ---
    if (i + 1) % BATCH_SIZE == 0:         # [cite: 251]
        if etudiants_batch:
            etudiants_col.insert_many(etudiants_batch) # [cite: 253]
        if notes_batch:
            notes_col.insert_many(notes_batch)         # [cite: 254]
        
        # Vider les listes pour le prochain lot
        etudiants_batch = []              # [cite: 252]
        notes_batch = []                  # [cite: 255]
        print(f"... {i+1} etudiants inseres.") # [cite: 256]

# --- Insertion du reste (si pas multiple de 10000) ---
if etudiants_batch:                       # [cite: 260]
    etudiants_col.insert_many(etudiants_batch) # [cite: 262]
if notes_batch:                           # [cite: 263]
    notes_col.insert_many(notes_batch)    # [cite: 265]

end_time = time.time()                    # [cite: 267]
print("--- Generation Terminee ---")      # [cite: 270]
print(f"Temps total: {end_time - start_time:.2f} secondes") # [cite: 271]