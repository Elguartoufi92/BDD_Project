// =================================================================
// SCRIPT DE CONFIGURATION MONGODB
// SCENARIO B: Sharding par "annee_universitaire"
// Rôle: Abdelkabir (Role 3)
// =================================================================

print("===== Début Configuration Sharding (SCENARIO B: ANNEE) =====");

// Mol-a7aDa: L-commandes dyal rs.initiate() ma kayninch hna.
// Kaynin f script l-kbir (run_project.sh) 7it kayt-daro ghir merra wa7da.

print("1. Ajout Shard A (shardA-rs) au Cluster...");
sh.addShard("shardA-rs/shA1:27017,shA2:27017");

print("2. Ajout Shard B (shardB-rs) au Cluster...");
sh.addShard("shardB-rs/shB1:27017,shB2:27017");

print("... Shards ajoutés avec succès.");

print("3. Activation Sharding sur la DB 'universiteDB'...");
try {
    sh.enableSharding("universiteDB");
    print("   ... 'universiteDB' activée pour le sharding.");
} catch (e) {
    print("   ... DB 'universiteDB' déjà activée.");
}

print("4. Configuration Sharding (par ANNEE) sur les collections...");

// Shard 'etudiants'
try {
    sh.shardCollection("universiteDB.etudiants", { annee_universitaire: 1 });
    print("   ... Collection 'etudiants' shardée par 'annee_universitaire'.");
} catch (e) {
    print("   ... ERREUR ou Collection 'etudiants' déjà shardée.");
    printjson(e);
}

// Shard 'notes'
try {
    sh.shardCollection("universiteDB.notes", { annee_universitaire: 1 });
    print("   ... Collection 'notes' shardée par 'annee_universitaire'.");
} catch (e) {
    print("   ... ERREUR ou Collection 'notes' déjà shardée.");
    printjson(e);
}


print("===== Configuration Terminée (SCENARIO B) =====");
print("\nVérification du statut du cluster:");
sh.status();