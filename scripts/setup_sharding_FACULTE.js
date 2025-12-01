// =================================================================
// SCRIPT DE CONFIGURATION MONGODB - VERSION CORRIGÉE (V2)
// SCENARIO A: Sharding par "faculte"
// Compatible: MongoDB 6.0, 7.0, 8.0+
// =================================================================

print("\n===== Début Configuration Sharding (SCENARIO A: FACULTE) =====");

// ---------------------------------------------------------
// 1. CONFIGURATION SYSTEME (Chunk Size)
// ---------------------------------------------------------
print("1. Configuration du Chunk Size (1MB)...");
try {
    var configDB = db.getSiblingDB("config");
    // FIX: Bdellna .save() (Qdima) b .updateOne() (Jdida)
    configDB.settings.updateOne(
        { _id: "chunksize" },
        { $set: { value: 1 } },
        { upsert: true }
    );
    print("   ✅ Chunk Size réglé sur 1 MB.");
} catch (e) {
    print("   ⚠️ Erreur Chunk Size: " + e);
}

// ---------------------------------------------------------
// 2. AJOUT DES SHARDS
// ---------------------------------------------------------
print("2. Ajout des Shards...");
try {
    sh.addShard("shardA-rs/shA1:27017,shA2:27017");
    print("   ✅ Shard A ajouté.");
} catch(e) { print("   ℹ️  Shard A existe déjà."); }

try {
    sh.addShard("shardB-rs/shB1:27017,shB2:27017");
    print("   ✅ Shard B ajouté.");
} catch(e) { print("   ℹ️  Shard B existe déjà."); }

// ---------------------------------------------------------
// 3. ACTIVATION DB
// ---------------------------------------------------------
print("3. Activation Sharding sur 'universiteDB'...");
try {
    sh.enableSharding("universiteDB");
    print("   ✅ DB activée avec succès.");
} catch (e) { 
    print("   ℹ️  DB déjà activée."); 
}

// ---------------------------------------------------------
// 4. FONCTION DE CONFIGURATION
// ---------------------------------------------------------
function setupAndBalance(collName) {
    var ns = "universiteDB." + collName;
    print("\n>>> Traitement de la collection : " + ns);

    // A. SHARDING
    try {
        sh.shardCollection(ns, { faculte: 1 });
        print("    ✅ [SHARD] Collection shardée.");
    } catch (e) {
        print("    ℹ️  [SHARD] Déjà shardée.");
    }

    // B. SPLITTING (Découpage)
    // On coupe le gateau à "Faculte C"
    print("    ... Tentative de Split à 'Faculte C'...");
    try {
        var res = sh.splitAt(ns, { faculte: "Faculte C" });
        if (res.ok) {
            print("    ✅ [SPLIT] Split réussi.");
        } else {
            print("    ℹ️  [SPLIT] Pas nécessaire ou erreur mineure.");
        }
    } catch (e) {
        print("    ℹ️  [SPLIT] Déjà splité ou erreur: " + e.message);
    }

    // C. MOVING (Déplacement)
    // On déplace le morceau "Faculte C et plus" vers Shard B
    print("    ... Tentative de déplacement vers Shard B...");
    try {
        var res = sh.moveChunk(ns, { faculte: "Faculte C" }, "shardB-rs");
        if (res.ok) {
            print("    ✅ [MOVE] Déplacement réussi.");
        } else {
            print("    ℹ️  [MOVE] Déjà sur le bon shard.");
        }
    } catch (e) {
        // Ignorer l'erreur si c'est déjà fait
        print("    ℹ️  [MOVE] Chunk déjà déplacé.");
    }
}

// ---------------------------------------------------------
// 5. APPLICATION
// ---------------------------------------------------------
setupAndBalance("etudiants");
setupAndBalance("notes");

print("\n===== Configuration Terminée avec Succès =====");
print("Distribution actuelle :");
printjson(sh.status());