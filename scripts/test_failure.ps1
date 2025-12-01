# ============================================
#  TEST DE TOLERANCE AUX PANNES (PowerShell)
#  Author: Wissal
# ============================================

$PRIMARY_NODE = "shA1"
$SCRIPT_DIR = $PSScriptRoot
$PYTHON_SCRIPT = "$SCRIPT_DIR\..\python_queries\run_queries.py"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   TEST DE TOLERANCE AUX PANNES - WISSAL"
Write-Host "============================================"
Write-Host ""

# --- 1. Test AVANT la panne ---
Write-Host "1. Test AVANT panne..." -ForegroundColor Yellow
python $PYTHON_SCRIPT

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR : Les requêtes ne fonctionnent même pas avant la panne !" -ForegroundColor Red
    exit 1
}
Write-Host "OK : Requêtes fonctionnelles avant la panne." -ForegroundColor Green

# --- 2. Simulation de la panne ---
Write-Host "2. Simulation de la panne (Arrêt de $PRIMARY_NODE)..." -ForegroundColor Yellow
docker stop $PRIMARY_NODE
Start-Sleep -Seconds 5

# --- 3. Attente de l'élection ---
Write-Host "3. Attente de l'élection (15s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# --- 4. Test PENDANT la panne ---
Write-Host "4. Test PENDANT panne..." -ForegroundColor Yellow
python $PYTHON_SCRIPT

if ($LASTEXITCODE -ne 0) {
    Write-Host "ECHEC : Le cluster NE SURVIT PAS à la panne !" -ForegroundColor Red
    # N3awdo nche3lo l node wakha fchlna
    docker start $PRIMARY_NODE
    exit 1
}
Write-Host "OK : Le cluster fonctionne malgré la panne !" -ForegroundColor Green

# --- 5. Redémarrage ---
Write-Host "5. Redémarrage du noeud..." -ForegroundColor Yellow
docker start $PRIMARY_NODE
Start-Sleep -Seconds 5
Write-Host "Noeud redémarré."

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "    TEST DE TOLERANCE AUX PANNES REUSSI "
Write-Host "============================================" -ForegroundColor Cyan