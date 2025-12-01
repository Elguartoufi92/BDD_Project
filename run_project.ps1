# =================================================
# Master script to run the entire project (PowerShell Version)
# Author: Wissal
# =================================================

$ErrorActionPreference = "Stop"  # Stop on error (Bhal set -e f bash)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "     STARTING FULL PROJECT WORKFLOW"
Write-Host "============================================" -ForegroundColor Cyan
Start-Sleep -Seconds 5

# -------------------------------------------------
# Step 0 : Copy required scripts BEFORE anything
# -------------------------------------------------
# Start containers first to be able to copy files

Write-Host "---[STEP 0] Starting cluster and copying required scripts into containers---" -ForegroundColor Yellow


# Copy JS config files
docker cp ./scripts/init-config-rs.js cfg1:/scripts/init-config-rs.js
docker cp ./scripts/init-shardA-rs.js shA1:/scripts/init-shardA-rs.js
docker cp ./scripts/init-shardB-rs.js shB1:/scripts/init-shardB-rs.js
docker cp ./scripts/setup_sharding_FACULTE.js mongos:/scripts/setup_sharding_FACULTE.js

# Copy Bash script for tests
docker cp ./scripts/test_failure.sh mongos:/scripts/test_failure.sh

Write-Host "Scripts copied successfully."
Write-Host ""

# -------------------------------------------------
# Step 1 : Start Docker Cluster
# -------------------------------------------------
Write-Host "---[STEP 1] Verify Cluster---" -ForegroundColor Yellow
docker-compose up -d

Write-Host "Waiting 10s for cluster to stabilize..."
Start-Sleep -Seconds 10

# -------------------------------------------------
# Step 2 : Config Server Initialization
# -------------------------------------------------
Write-Host "---[STEP 2] Initializing Config Server---" -ForegroundColor Yellow
# PowerShell ma kaysta3mlch '<', walakin hit copina l'fichier l dakhil, nqdro n3ayto 3lih direct
docker exec cfg1 mongosh --file /scripts/init-config-rs.js

# -------------------------------------------------
# Step 3 : Shard A Initialization
# -------------------------------------------------
Write-Host "---[STEP 3] Initializing Shard A---" -ForegroundColor Yellow
docker exec shA1 mongosh --file /scripts/init-shardA-rs.js

# -------------------------------------------------
# Step 4 : Shard B Initialization
# -------------------------------------------------
Write-Host "---[STEP 4] Initializing Shard B---" -ForegroundColor Yellow
docker exec shB1 mongosh --file /scripts/init-shardB-rs.js

# -------------------------------------------------
# Step 5 : Sharding Setup
# -------------------------------------------------
Write-Host "---[STEP 5] Setting up Sharding (FACULTE)---" -ForegroundColor Yellow
docker exec mongos mongosh --file /scripts/setup_sharding_FACULTE.js

Write-Host "Waiting 20s for cluster to stabilize..."
Start-Sleep -Seconds 20
docker exec mongos mongosh --file /scripts/setup_sharding_FACULTE.js

# -------------------------------------------------
# Step 6 :  Data generation
# -------------------------------------------------
Write-Host "---[STEP 6] Generating Sample Data---" -ForegroundColor Yellow
# Nta2ked anna Python kheddam
python data_generator/generate_data.py

# -------------------------------------------------
# Step 7 : Fault Tolerance Test
# -------------------------------------------------
Write-Host "---[STEP 7] Testing Fault Tolerance---" -ForegroundColor Yellow
# Hna runnina l'script DAKHEL container bach netfadaw machakim dyal Windows/Path
.\scripts\test_failure.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "      PROJECT WORKFLOW COMPLETE "
Write-Host "============================================" -ForegroundColor Cyan