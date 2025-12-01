// =================================================================
// SCRIPT DE CONFIGURATION MONGODB - VERSION ULTIME (AUTO-BALANCE)
// SCENARIO A: Sharding par "faculte"
// Rôle: Abdelkabir (Role 3)
// =================================================================

print("===== Début Configuration Sharding (SCENARIO A: FACULTE) =====");

// ---------------------------------------------------------
// 1. CONFIGURATION SYSTEME (Chunk Size)
// ---------------------------------------------------------
print("0. Forçage du Chunk Size à 1MB (Pour les petites données)...");
try {
    var configDB = db.getSiblingDB("config");
    configDB.settings.save({ _id: "chunksize", value: 1 });
    print("   ... Chunk Size réglé sur 1 MB avec succès!");
} catch (e) {
    print("   ... Erreur Chunk Size (ou déjà fait): " + e);
}

// ---------------------------------------------------------
// 2. AJOUT DES SHARDS
// ---------------------------------------------------------
print("1. Ajout des Shards...");
try {
    sh.addShard("shardA-rs/shA1:27017,shA2:27017");
    print("   ... Shard A ajouté.");
} catch(e) { print("   ... Shard A existe déjà."); }

try {
    sh.addShard("shardB-rs/shB1:27017,shB2:27017");
    print("   ... Shard B ajouté.");
} catch(e) { print("   ... Shard B existe déjà."); }

// ---------------------------------------------------------
// 3. ACTIVATION DB & SHARDING BASIQUE
// ---------------------------------------------------------
print("3. Activation Sharding sur 'universiteDB'...");
try {
    sh.enableSharding("universiteDB");
} catch (e) { print("   ... DB déjà activée."); }

// Fonction pour sharder et équilibrer une collection
function setupAndBalance(collName) {
    var ns = "universiteDB." + collName;
    print("\n>>> Configuration de : " + ns);

    // A. Sharding Key
    try {
        sh.shardCollection(ns, { faculte: 1 });
        print("    [OK] Collection shardée.");
    } catch (e) {
        print("    [INFO] Déjà shardée.");
    }

    // B. PRE-SPLITTING (Hna l'Qaleb: Kan-qsmo l'Tariq qbel ma tji l'data)
    // On coupe le gateau à "Faculte C".
    // Résultat: 
    //   Chunk 1: -Infini ... Faculte C (Contient Faculte A, B)
    //   Chunk 2: Faculte C ... +Infini (Contient Faculte C, D)
    print("    [SPLIT] Découpage manuel à 'Faculte C'...");
    try {
        sh.splitAt(ns, { faculte: "Faculte C" });
        print("    [OK] Split réussi.");
    } catch (e) {
        print("    [INFO] Déjà splité.");
    }

    // C. MOVE CHUNK (Te7wal)
    // On déplace le morceau "Faculte C et plus" vers Shard B
    print("    [MOVE] Déplacement des Facultés C/D vers Shard B...");
    try {
        sh.moveChunk(ns, { faculte: "Faculte C" }, "shardB-rs");
        print("    [OK] Déplacement réussi.");
    } catch (e) {
        print("    [INFO] Déjà déplacé ou erreur (voir logs).");
    }
}

// ---------------------------------------------------------
// 4. EXECUTION SUR LES COLLECTIONS
// ---------------------------------------------------------
print("4. Application sur les collections...");

setupAndBalance("etudiants");
setupAndBalance("notes");

// ---------------------------------------------------------
// 5. DEMARRAGE BALANCER
// ---------------------------------------------------------
print("5. Activation du Balancer (au cas où)...");
printjson(sh.startBalancer());

print("\n===== Configuration ULTIME Terminée =====");
print("Distribution actuelle :");
var universiteDB = db.getSiblingDB("universiteDB");
printjson(universiteDB.etudiants.getShardDistribution());