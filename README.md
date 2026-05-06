# 🏛️ Distributed University Database System (BDD_Project)

## 📋 Project Overview

This is a **distributed database system** designed for a university using **MongoDB Sharded Cluster** architecture. It demonstrates enterprise-level database design with fault tolerance, data replication, and horizontal scalability using sharding strategies.

### Key Features:
- **MongoDB Sharded Cluster** with multiple replica sets
- **FastAPI REST API** for database operations
- **Streamlit Dashboard** for real-time cluster monitoring and chaos testing
- **Data Generation** capabilities for testing with synthetic university data (students & grades)
- **Fault Tolerance Testing** with read preference strategies
- **Two Sharding Scenarios**: By Faculty (FACULTE) or Academic Year (ANNEE)

---

## 🏗️ Architecture

### Infrastructure Components

```
┌─────────────────────────────────────────────────┐
│         Mongos Router (Port 27018)              │
│      (Single entry point for application)       │
└──────────────┬──────────────────────────────────┘
               │
      ┌────────┴────────┐
      │                 │
      ▼                 ▼
┌──────────────┐  ┌──────────────┐
│ Shard A RS   │  │ Shard B RS   │
│ (Faculty A&B)│  │ (Faculty C&D)│
│ shA1, shA2   │  │ shB1, shB2   │
└──────────────┘  └──────────────┘
      │                 │
      └────────┬────────┘
               │
      ┌────────▼────────┐
      │  Config Servers │
      │  cfg1, cfg2     │
      │  (Metadata)     │
      └─────────────────┘
```

### Container Services (Docker Compose)

| Service | Role | Port | Description |
|---------|------|------|-------------|
| **cfg1, cfg2** | Config Servers | 30001, 30002 | Metadata storage (Replica Set: cfg-rs) |
| **shA1, shA2** | Shard A | 30003, 30004 | Data partition A (Replica Set: shardA-rs) |
| **shB1, shB2** | Shard B | 30005, 30006 | Data partition B (Replica Set: shardB-rs) |
| **mongos** | Router | 27018 | Query router & entry point |

---

## 📦 Technology Stack

### Backend
- **MongoDB** (Latest): NoSQL database with sharding support
- **FastAPI**: Modern, fast Python web framework
- **Uvicorn**: ASGI web server
- **PyMongo**: MongoDB driver for Python

### Frontend & Monitoring
- **Streamlit**: Interactive data dashboard
- **Plotly**: Advanced data visualization
- **Pandas**: Data manipulation and analysis
- **Matplotlib**: Chart generation

### Data Generation
- **Faker**: Synthetic data generation (French locale)

### Infrastructure
- **Docker & Docker Compose**: Containerization and orchestration

---

## 📁 Project Structure

```
BDD_Project/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── docker-compose.yml                 # MongoDB cluster configuration
│
├── api.py                             # FastAPI REST API server
├── dashboard.py                       # Streamlit monitoring dashboard
├── debug_shard.py                     # Sharding configuration detection
│
├── data_generator/
│   └── generate_data.py              # Synthetic data generation (5000 students)
│
├── python_queries/
│   └── run_queries.py                # Benchmark & chaos testing queries
│
├── scripts/
│   ├── init-config-rs.js             # Initialize config replica set
│   ├── init-shardA-rs.js             # Initialize Shard A replica set
│   ├── init-shardB-rs.js             # Initialize Shard B replica set
│   ├── setup_sharding_ANNEE.js       # Enable sharding by academic year
│   ├── setup_sharding_FACULTE.js     # Enable sharding by faculty
│   └── test_failure.ps1              # PowerShell chaos testing script
│
└── run_project.ps1                    # Main startup script (Windows)
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Docker** and **Docker Compose** (version 3.8+)
- **Python 3.8+**
- **Git** (optional)

### 1. Start MongoDB Cluster

```bash
# Navigate to project directory
cd BDD_Project

# Start all containers
docker-compose up -d

# Verify all services are healthy
docker-compose ps
```

**Expected Output:**
```
CONTAINER ID   STATUS
cfg1           healthy
cfg2           healthy
shA1           healthy
shA2           healthy
shB1           healthy
shB2           healthy
mongos         healthy
```

### 2. Initialize Cluster Configuration

Choose **ONE** sharding scenario:

#### Option A: Shard by Academic Year (ANNEE)
```bash
docker exec -it mongos mongosh <<EOF
load("/scripts/init-config-rs.js")
load("/scripts/init-shardA-rs.js")
load("/scripts/init-shardB-rs.js")
load("/scripts/setup_sharding_ANNEE.js")
EOF
```

#### Option B: Shard by Faculty (FACULTE)
```bash
docker exec -it mongos mongosh <<EOF
load("/scripts/init-config-rs.js")
load("/scripts/init-shardA-rs.js")
load("/scripts/init-shardB-rs.js")
load("/scripts/setup_sharding_FACULTE.js")
EOF
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Generate Test Data

```bash
python data_generator/generate_data.py
```

This will:
- Create 5,000 students with 5 grades each (25,000 total documents)
- Distribute data across shards based on your chosen key
- Print progress every 500 insertions

### 5. Run the API Server

```bash
python api.py
```

Server will be available at: `http://localhost:8000`

### 6. Launch the Dashboard

In a **new terminal**:
```bash
streamlit run dashboard.py
```

Dashboard will open at: `http://localhost:8501`

---

## 🔌 API Endpoints

### Health & Monitoring
- **GET** `/` - Health check
- **GET** `/cluster-full-stats` - Cluster statistics and distribution

### Data Operations
- **GET** `/read-note` - Read student grade (Fault tolerance test)
- **GET** `/etudiants/{etudiant_id}` - Get student by ID
- **GET** `/notes/{etudiant_id}` - Get all grades for a student

---

## 📊 Dashboard Features

### Tab 1: Chaos Testing 🔥
- **Test Read Operations** with fault tolerance
- Monitor response times during failures
- Verify PRIMARY_PREFERRED read strategy
- Real-time status indicators

### Tab 2: Cluster Statistics 📊
- View data distribution across shards
- Monitor document counts per shard
- Visualize sharding effectiveness
- Collection metadata display

---

## 🔍 Data Model

### Collections

#### etudiants (Students)
```json
{
  "_id": ObjectId,
  "etudiant_id": "CNE_1",
  "nom": "Dupont",
  "prenom": "Jean",
  "faculte": "Faculte A",
  "annee_universitaire": "2023-2024"
}
```

#### notes (Grades)
```json
{
  "_id": ObjectId,
  "etudiant_id": "CNE_1",
  "module": "Module_1",
  "note": 15.50,
  "faculte": "Faculte A",           // Denormalized for sharding
  "annee_universitaire": "2023-2024" // Denormalized for sharding
}
```

### Sharding Keys
- **ANNEE Mode**: `annee_universitaire` (e.g., "2023-2024")
- **FACULTE Mode**: `faculte` (e.g., "Faculte A", "Faculte B", "Faculte C", "Faculte D")

---

## 🧪 Testing & Benchmarking

### Normal Mode (Performance Benchmarking)
```bash
python python_queries/run_queries.py
```
- Uses PRIMARY read preference
- Enables database indexes
- Measures standard performance

### Chaos Mode (Fault Tolerance Testing)
```bash
python python_queries/run_queries.py --chaos
```
- Uses PRIMARY_PREFERRED read preference
- Disables index creation
- Simulates primary failures
- Tests cluster failover capabilities

---

## 🛠️ Configuration Details

### MongoDB Configuration

**Chunk Size:** 1 MB (configurable in setup scripts)

**Read Preferences:**
- **Normal Mode**: PRIMARY (read only from primary)
- **Chaos Mode**: PRIMARY_PREFERRED (read from secondary if primary unavailable)

**Timeouts:**
- Server Selection: 2000-5000 ms
- Connection: 5000 ms

### Faculties & Academic Years

**Faculties:**
- Faculte A
- Faculte B
- Faculte C
- Faculte D

**Academic Years:**
- 2022-2023
- 2023-2024
- 2024-2025

**Modules:**
- Module_1 through Module_5

---

## 📈 Performance Characteristics

### Data Generation
- **5,000 students** with 5 grades each = 25,000 documents
- **Batch insertion** (500-document chunks) for optimal performance
- Average generation time: ~20-30 seconds

### Sharding Strategy
- **2 shards** (Shard A & B) for parallel processing
- **2 replicas per shard** for fault tolerance
- **Automatic chunk distribution** across shards

---

## 🔐 Security Considerations

- Currently configured for **development/testing only**
- No authentication enabled (add credentials in production)
- Uses Docker internal networking (cluster-net)
- Bind to 0.0.0.0 for Docker compatibility (restrict in production)

---

## 🐛 Troubleshooting

### Issue: "Connection Refused"
```bash
# Verify containers are running
docker-compose ps

# Check logs
docker-compose logs mongos
```

### Issue: "Collection doesn't exist"
```bash
# Re-run data generation
python data_generator/generate_data.py
```

### Issue: "Sharding index not found"
```bash
# Re-initialize the setup scripts for your chosen scenario
# See "Initialize Cluster Configuration" section above
```

### Issue: "Primary server down" (in Chaos mode)
- This is **expected behavior** - read operations should succeed via replica
- Check that PRIMARY_PREFERRED strategy is in use

---

## 📚 Learning Resources

### Key Concepts Demonstrated
1. **Horizontal Scalability** via sharding
2. **High Availability** via replica sets
3. **Distributed Systems** architecture patterns
4. **Fault Tolerance** strategies
5. **Data Denormalization** for sharding efficiency
6. **Read Preference** configurations
7. **Batch Operations** for performance

### MongoDB Documentation
- [Sharding](https://docs.mongodb.com/manual/sharding/)
- [Replica Sets](https://docs.mongodb.com/manual/replication/)
- [Read Preferences](https://docs.mongodb.com/manual/core/read-preference/)

---

## 📝 Notes

- **Data Denormalization**: Faculty and academic year are duplicated in the notes collection to support efficient sharding queries
- **Docker Network**: All services communicate via the "cluster-net" bridge network
- **Mongos Router**: Single entry point (port 27018 externally, 27017 internally) handles all routing
- **Config Servers**: CRITICAL - losing both cfg1 and cfg2 will make the cluster unaware of shard configuration

---

## 👥 Contributors & Roles

- **Role 1** - Architecture design and cluster setup
- **Role 2** - API and data integration
- **Role 3** - Sharding configuration and optimization
- **Role 4** - Dashboard and monitoring (Streamlit)

---

## 📄 License

This project is for educational purposes.

---

## 🎯 Future Enhancements

- [ ] Add MongoDB authentication (username/password)
- [ ] Implement write operations (POST, PUT, DELETE)
- [ ] Add transaction support for multi-shard operations
- [ ] Real-time monitoring with Prometheus + Grafana
- [ ] Automated backup and restore procedures
- [ ] Performance tuning for large datasets (100M+ documents)
- [ ] Load balancing for multi-region deployment

---

## ❓ FAQ

**Q: Why denormalize faculty and year in notes?**
A: MongoDB sharding requires the shard key to be present in every document for efficient routing.

**Q: Can I add more shards later?**
A: Yes! MongoDB supports dynamic shard addition. Use `sh.addShard()` to add new replica sets.

**Q: What happens if the primary shard fails?**
A: In PRIMARY_PREFERRED mode, reads automatically failover to secondaries. The replica set handles automatic primary election.

**Q: How is data actually distributed?**
A: MongoDB automatically splits the shard key range into chunks and distributes them across shards using the shard key values.

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review MongoDB logs: `docker-compose logs <service>`
3. Verify all containers are healthy: `docker-compose ps`
4. Check Python requirements are installed: `pip list`

---

**Last Updated:** May 2026  
**Project Status:** ✅ Active Development
