#!/bin/bash
# =================================================
# Master script to run the entire project
# Author: Wissal
# =================================================

set -e  # Stop on error

echo "============================================"
echo "     STARTING FULL PROJECT WORKFLOW"
echo "============================================"

# -------------------------------------------------
# Step 0 : Copy required scripts BEFORE anything
# -------------------------------------------------
echo "---[STEP 0] Copying required scripts into containers---"

# Always use relative paths with ./ to avoid ENOENT on Windows/Git Bash
docker cp ./scripts/init-config-rs.js cfg1:/scripts/init-config-rs.js
docker cp ./scripts/init-shardA-rs.js shA1:/scripts/init-shardA-rs.js
docker cp ./scripts/init-shardB-rs.js shB1:/scripts/init-shardB-rs.js
docker cp ./scripts/setup_sharding_FACULTE.js mongos:/scripts/setup_sharding_FACULTE.js

# Copy Python query script for tests
docker cp ./scripts/test_failure.sh mongos:/scripts/test_failure.sh

echo "Scripts copied successfully."
echo ""

# -------------------------------------------------
# Step 1 : Start Docker Cluster
# -------------------------------------------------
echo "---[STEP 1] Starting Cluster---"
docker-compose up -d
echo "Waiting 30s for cluster to stabilize..."
sleep 30

# -------------------------------------------------
# Step 2 : Config Server Initialization
# -------------------------------------------------
echo "---[STEP 2] Initializing Config Server---"
docker exec -i cfg1 mongosh < ./scripts/init-config-rs.js


# -------------------------------------------------
# Step 3 : Shard A Initialization
# -------------------------------------------------
echo "---[STEP 3] Initializing Shard A---"
docker exec -i shA1 mongosh < ./scripts/init-shardA-rs.js

# -------------------------------------------------
# Step 4 : Shard B Initialization
# -------------------------------------------------
echo "---[STEP 4] Initializing Shard B---"
docker exec -i shB1 mongosh < ./scripts/init-shardB-rs.js

# -------------------------------------------------
# Step 5 : Sharding Setup
# -------------------------------------------------
echo "---[STEP 5] Setting up Sharding (FACULTE)---"
docker exec -i mongos mongosh < ./scripts/setup_sharding_FACULTE.js

# -------------------------------------------------
# Step 6 :  Data generation
# -------------------------------------------------

echo "---[STEP 7] Generating Sample Data---"
py -3 ./data_generator/generate_data.py

# -------------------------------------------------
# Step 8 : Fault Tolerance Test
# -------------------------------------------------
echo "---[STEP 8] Testing Fault Tolerance---"
bash ./scripts/test_failure.sh

echo "============================================"
echo "      PROJECT WORKFLOW COMPLETE "
echo "============================================"
