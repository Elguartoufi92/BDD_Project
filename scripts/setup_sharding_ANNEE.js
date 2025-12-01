// =================================================================
// SCRIPT DE CONFIGURATION MONGODB - SCENARIO B (ANNEE) - FORCE
// Rôle: Abdelkabir (Role 3)
// =================================================================

print("===== Début Configuration Sharding (SCENARIO B: ANNEE) =====");

// ---------------------------------------------------------
// 1. CONFIGURATION SYSTEME (Chunk Size 1MB)
// ---------------------------------------------------------
print("0. Forçage du Chunk Size à 1MB...");
try {
    var configDB = db.getSiblingDB("config");
    configDB.settings.save({ _id: "chunksize", value: 1 });
    print("   ... [OK] Chunk Size réglé sur 1 MB.");
} catch (e) {
    print("   ... [INFO] Erreur Chunk Size (ou déjà fait).");
}

// ---------------------------------------------------------
// 2. AJOUT DES SHARDS
// ---------------------------------------------------------
print("1. Ajout des Shards...");
try { sh.addShard("shardA-rs/shA1:27017,shA2:27017"); } catch(e) {}
try { sh.addShard("shardB-rs/shB1:27017,shB2:27017"); } catch(e) {}
print("   ... [OK] Shards vérifiés.");

// ---------------------------------------------------------
// 3. ACTIVATION DB
// ---------------------------------------------------------
print("3. Activation Sharding sur 'universiteDB'...");
try { sh.enableSharding("universiteDB"); } catch (e) {}

// ---------------------------------------------------------
// 4. FONCTION MAGIQUE (SHARD + SPLIT + MOVE)
// ---------------------------------------------------------
function forceShardingByYear(collName) {
    var ns = "universiteDB." + collName;
    print("\n>>> Traitement de la collection : " + collName);

    // A. Sharding Key
    try {
        sh.shardCollection(ns, { annee_universitaire: 1 });
        print("    [SHARD] Collection shardée.");
    } catch (e) { print("    [INFO] Déjà shardée."); }

    // B. SPLIT (Qsem l'Gâteau à "2024-2025")
    // Chunk 1: < 2024-2025 (Ex: 2022, 2023) -> Ibqa f Shard A
    // Chunk 2: >= 2024-2025 (Ex: 2024, 2025) -> Imchi l Shard B
    print("    [SPLIT] Découpage manuel à '2024-2025'...");
    try {
        var res = sh.splitAt(ns, { annee_universitaire: "2024-2025" });
        if(res.ok) print("    [OK] Split réussi.");
        else print("    [INFO] Message Split: " + res.errmsg);
    } catch (e) { print("    [INFO] Erreur Split (déjà fait?)."); }

    // C. MOVE (Re77el l Shard B)
    print("    [MOVE] Déplacement de '2024-2025+' vers Shard B...");
    try {
        var res = sh.moveChunk(ns, { annee_universitaire: "2024-2025" }, "shardB-rs");
        if(res.ok) print("    [OK] Déplacement réussi.");
        else print("    [INFO] Message Move: " + res.errmsg);
    } catch (e) { print("    [INFO] Erreur Move (déjà déplacé?)."); }
}

// ---------------------------------------------------------
// 5. EXECUTION
// ---------------------------------------------------------
forceShardingByYear("etudiants");
forceShardingByYear("notes");

// ---------------------------------------------------------
// 6. FIN
// ---------------------------------------------------------
print("6. Démarrage du Balancer...");
sh.startBalancer();

print("\n===== Configuration SCENARIO B (FORCE) Terminée =====");
print("Distribution actuelle :");
var universiteDB = db.getSiblingDB("universiteDB");
universiteDB.etudiants.getShardDistribution();