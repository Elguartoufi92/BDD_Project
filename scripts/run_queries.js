console.log("SCRIPT LANCÉ");

use universiteDB;

// Compter les documents et afficher
var count = db.etudiants.count();
print("Nombre d'étudiants :", count);