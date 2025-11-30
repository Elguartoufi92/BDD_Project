#!/bin/bash

# Get absolute path of BDD_PROJECT
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"

PRIMARY_NODE="shA1"

echo "============================================"
echo "   TEST DE TOLERANCE AUX PANNES - WISSAL"
echo "============================================"
echo ""

# --- 1️⃣ Test AVANT la panne ---
echo "Test AVANT panne..."
py -3 "$BASE_DIR/python_queries/run_queries.py"

if [ $? -ne 0 ]; then
    echo "ERREUR : Les requêtes ne fonctionnent même pas avant la panne !"
    exit 1
fi
echo "OK : Requêtes fonctionnelles avant la panne."

# --- 2️⃣ Simulation de la panne ---
docker stop $PRIMARY_NODE
sleep 5

# --- 3️⃣ Attente de l'élection ---
sleep 15

# --- 4️⃣ Test PENDANT la panne ---
echo "Test PENDANT panne..."
py -3 "$BASE_DIR/python_queries/run_queries.py"

if [ $? -ne 0 ]; then
    echo "Le cluster NE SURVIT PAS à la panne !"
    exit 1
fi
echo "OK : Le cluster fonctionne malgré la panne !"

# --- 5️⃣ Redémarrage ---
docker start $PRIMARY_NODE
sleep 5
echo "Noeud redémarré."

echo "============================================"
echo "    TEST DE TOLERANCE AUX PANNES REUSSI "
echo "============================================"
