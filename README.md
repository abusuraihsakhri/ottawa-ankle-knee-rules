# OTTAWA Ankle Knee Rules

> **Domain:** Clinical Decision Support & Biomedical Computing  
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Ottawa Ankle & Knee Rules Decision Engine evaluates clinical criteria to rule out unnecessary radiography in acute ankle, midfoot, and knee injuries. It provides a multi-worker agent architecture with PHI protection, cryptographic audit trails, and both CLI and REST API interfaces.

Author: Dr. Abu Suraih Sakhri
License: MIT

---

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/ottawa-ankle-knee-rules.git
cd ottawa-ankle-knee-rules

# Install dependencies
pip install fastapi uvicorn pydantic pytest
```

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Analytical Functions

- **`calculate_metrics()`**: Core scoring algorithm that computes weighted scores and classifies results into risk tiers.
- **`process_single()`**: Evaluates a single case with provided parameters.
- **`process_batch()`**: Processes CSV files with multiple records (includes path traversal protection).
- **`main()`**: CLI entry point with subcommands for single/batch evaluation.

### 🤖 Multi-Worker Agent Architecture

- **InvariantQCWorker**: Monitors primary metric thresholds and triggers alerts when exceeded.
- **SafetyEscalationWorker**: Handles critical safety interlocks and emergency escalation.
- **ProtocolConformanceWorker**: Detects protocol violations and discordant status descriptors.

---

## 💻 CLI Quickstart & Usage

### 1. Single Case Evaluation
```bash
python ottawa_rules.py single --v1 12.0 --v2 4.0 --v3 2.0
```

### 2. Batch CSV Processing
```bash
python ottawa_rules.py batch -i input.csv -o results.csv
```

### 3. Enterprise CLI (requires AUDIT_SECRET_KEY)
```bash
# Set the audit secret key (required for HMAC-SHA256 audit trail)
export AUDIT_SECRET_KEY="your-secure-audit-key"

# Run audit evaluation
python cli.py audit --task-id TASK-001 --primary 28.5 --secondary 14.2

# Batch processing
python cli.py batch -i input.csv -o results.csv

# Verify audit trail integrity
python cli.py verify-audit

# Start REST API server
python cli.py serve --host 127.0.0.1 --port 8000
```

### Input Data Schema (CSV)

| Field | Description | Requirement |
|:------|:------------|:------------|
| `Patient_ID` | Parameter / observation metric | Required |
| `v1` | Parameter / observation metric | Required |
| `v2` | Parameter / observation metric | Required |
| `v3` | Parameter / observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, DOBs, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation. Requires `AUDIT_SECRET_KEY` environment variable.
* **Path Traversal Protection:** All file operations validate and resolve paths to prevent directory traversal attacks.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
# Set a test audit key
export AUDIT_SECRET_KEY="test-audit-key"

# Run all tests
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t ottawa-ankle-knee-rules .
docker run -e AUDIT_SECRET_KEY="your-secure-key" -p 8000:8000 ottawa-ankle-knee-rules
```

Or using Docker Compose:

```bash
# Update docker-compose.yml with your secure AUDIT_SECRET_KEY
docker-compose up -d
```
