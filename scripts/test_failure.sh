#!/bin/bash

PRIMARY_NODE="shA1"
MONGOS_NODE="mongos"
QUERY_SCRIPT="/scripts/run_queries.js"   # <-- chemin **dans le conteneur**

echo "============================================"
echo "   TEST DE TOLERANCE AUX PANNES - WISSAL"
echo "============================================"
echo ""

# Copier le script dans le conteneur
docker exec -i $MONGOS_NODE mongosh < ./run_queries.js | grep -E '^[A-Z]'
echo "run_queries.js copié dans le conteneur."

# --- 1️⃣ Test AVANT la panne ---
docker exec -i $MONGOS_NODE mongosh < ./run_queries.js | grep "^\[direct: mongos\]"

if [ $? -ne 0 ]; then
    echo "ERREUR : Les requêtes ne fonctionnent même pas avant la panne !"
    exit 1
fi
echo "OK : Requêtes fonctionnelles avant la panne."

# --- 2️⃣ Simulation de la panne ---
docker stop $PRIMARY_NODE
sleep 5

# --- 3️⃣ Attente de la nouvelle élection ---
sleep 15

# --- 4️⃣ Test PENDANT la panne ---
docker exec -i $MONGOS_NODE mongosh < ./run_queries.js | grep "^\[direct: mongos\]"
if [ $? -ne 0 ]; then
    echo "Le cluster NE SURVIT PAS à la panne !"
    exit 1
fi
echo "OK : Le cluster fonctionne malgré la panne !"

# --- 5️⃣ Redémarrage du Primary ---
docker start $PRIMARY_NODE
sleep 5
echo "Noeud redémarré."

echo "============================================"
echo "    TEST DE TOLERANCE AUX PANNES REUSSI "
echo "============================================"
