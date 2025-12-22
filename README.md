# 📊 HCO Quant AI Platform: Agentic Financial & Threat Intelligence Dashboard

# 🌟 Project Overview

**HCO-Quant** is a high-performance, agentic platform built on **Jaseci 2.0 (Jaclang)**. It provides real-time quantitative trading signals, human-readable AI commentary, and integrated Threat Intelligence.

By utilizing Jaseci's **Object-Spatial Mapping**, the system orchestrates "Walkers" (Agents) that traverse a graph to perform complex financial analysis and security scans. This version represents a **Pure Jaseci implementation**, where the core intelligence and orchestration live entirely within `.jac` and `.jir` files.

# 🚀 Key Features

* **Agentic Graph Orchestration:** Uses Jaseci Walkers (`AssetOrchestrator`) to manage analysis logic as a traversal of data nodes.
* **AI Commentary (Powered by byLLM):** Direct integration within the Jac layer to generate natural language insights for every trading signal.
* **Threat Intelligence Agent:** A dedicated Jaseci Walker (`SecurityScanner`) that evaluates the safety of URLs and digital assets.
* **High-Speed Execution:** Built on Jaclang 0.9.x, leveraging the speed of the Jac Intermediate Representation (`.jir`) for near-instant agent deployment.
* **Decoupled Architecture:** A clean separation between the Backend Logic (`main.jac`) and the Client Interface (`app.jac`).

# 💻 Tech Stack

| Component | Technology | Role |
| --- | --- | --- |
| **Agentic Logic** | **Jaclang (Jaseci 2.0)** | Defines Walkers, Nodes, and Graph logic. |
| **Orchestration** | **byLLM** | Powers the AI-driven rationale within the Walkers. |
| **Runtime** | **Python 3.12 (venv)** | The underlying engine for Jaclang execution. |
| **Data Format** | **JIR (.jir)** | Pre-compiled Jac Intermediate Representation for fast loading. |

# ⚙️ Installation and Setup

### 1. Environment Preparation

The system requires Python 3.10+ and the Jaclang compiler.

```bash
# Navigate to the project root
cd ~/HCO-Quant

# Create and activate the virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Jaclang and byLLM
pip install jaclang byllm

```

### 2. Compilation (The Build Layer)

To ensure maximum speed, we compile the Jaseci backend into an intermediate representation:

```bash
# Set PYTHONPATH so the compiler can resolve internal paths
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Compile the main orchestrator
jac build backend/src/jac/main.jac

```

### 3. Environment Variables

Ensure your `.env` file exists in the root directory (but is ignored by git) to power the AI agents:

```bash
# .env
GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
VIRUSTOTAL_API_KEY="YOUR_VIRUSTOTAL_API_KEY_HERE"

```

# 👨‍💻 Usage and Execution

### Running the Agentic Client

The primary way to interact with the platform is via the Jaseci Client:

```bash
# Run the client walker
jac run frontend/src/app.jac

```

### Project Structure (Cleaned)

```text
HCO-Quant/
├── backend/
│   └── src/
│       └── jac/
│           ├── main.jac  <-- Master Orchestrator (Walkers & Nodes)
│           └── main.jir  <-- Compiled Agentic Logic
└── frontend/
    └── src/
        └── app.jac       <-- Client UI / Entry Point

```

# 🛡️ Security & Integrity

* **Zero-Leak Policy:** `.env`, `venv/`, and `.jaseci_logs` are strictly untracked via `.gitignore`.
* **Graph Isolation:** Data nodes (`Asset`) are encapsulated within the Jaseci graph, ensuring no raw financial data exposure.

# 🏁 Demo Instructions

1. **Start the Client:** Run `jac run frontend/src/app.jac`.
2. **Phase 1 (Quant):** Observe the `AssetOrchestrator` spawning for symbols like AAPL and TSLA. It will generate signals and AI commentary within the terminal.
3. **Phase 2 (Threat Intel):** Watch the `SecurityScanner` evaluate the safety of the configured test URLs.
4. **Graph Verification:** The output will confirm "Graph Persistence," meaning data has been successfully saved to the Jaseci memory layer.

