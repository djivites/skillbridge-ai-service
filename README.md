# 🚀 SkillBridge AI - Service Layer

![SkillBridge AI](https://img.shields.io/badge/SkillBridge-AI-0F172A?style=for-the-badge&logo=vercel&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776ab?style=for-the-badge&logo=python&logoColor=white)
![Neo4j](https://img.shields.io/badge/Neo4j-Graph%20DB-0081C2?style=for-the-badge&logo=neo4j&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Storage-FFF000?style=for-the-badge)

**SkillBridge AI Service** is the core intelligence engine of the platform. Built with Python and FastAPI, it leverages a **Multi-Agent Orchestration** model to perform semantic resume parsing, graph-based skill matching, and RAG-powered learning roadmap generation.

---

## 🛠️ Tech Stack
    
| Component | Technology |
|-----------|------------|
| **Framework** | ![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688?logo=fastapi&logoColor=white) |
| **Language** | ![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white) |
| **Graph Database** | ![Neo4j](https://img.shields.io/badge/Neo4j-Graph%20Aura-0081C2?logo=neo4j&logoColor=white) |
| **Vector Search** | ![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Cache-yellow) |
| **LLM Orchestration** | ![Groq](https://img.shields.io/badge/Groq-Llama--3.1-orange) ![Gemini](https://img.shields.io/badge/Gemini-Experimental-blue) |
| **Agents / RAG** | ![LangChain](https://img.shields.io/badge/LangChain-Framework-121212?logo=langchain) |
| **PDF Processing** | ![PyPDF](https://img.shields.io/badge/PyPDF-Parser-red) |

---

## 📁 Project Structure

```
skillbridge-ai-service/
├── skillbridge-ai-backend/     # Principal Python Service Directory
│   ├── agents/                 # Multi-Agent Workflow Logic
│   │   ├── skill_extractor.py  # LLM-based skill identification
│   │   └── roadmap_agent.py    # Learning path planning
│   ├── graph/                  # Neo4j Graph Interactions
│   │   ├── neo4j_client.py     # Connection management
│   │   ├── similarity.py       # Graph-based matching algorithms
│   │   └── skill_graph_builder.py # Prerequisite relationship logic
│   ├── llm/                    # LLM Client Wrappers
│   │   ├── groq_client.py      # Llama 3.1 integration
│   │   └── gemini_client.py    # Google Gemini integration
│   ├── rag/                    # Retrieval Augmented Generation
│   │   └── vector_store.py     # ChromaDB interactions
│   ├── services/               # Core Business Logic
│   │   └── roadmap_service.py  # End-to-end roadmap orchestration
│   ├── utils/                  # Shared Utilities
│   │   ├── pdf_loader.py       # Document parsing
│   │   └── logger.py           # Custom logging system
│   ├── main.py                 # FastAPI Entry Point
│   ├── requirements.txt        # Python Dependencies
│   └── test_api.py             # Diagnostic test suite
└── README.md                   # You are here
```

---

## 🚀 Quick Start

### **Prerequisites**
- Python 3.10 or higher
- Neo4j Aura Instance (or local Neo4j Desktop)
- Groq API Key (for high-speed inference)
- Google Gemini API Key

### **Step 1: Setup Environment**
Navigate to the service backend:
```bash
cd skillbridge-ai-service/skillbridge-ai-backend
```

Create a Virtual Environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### **Step 2: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 3: Configure Environment Variables**
Create a `.env` file in `skillbridge-ai-backend/`:
```bash
# LLM APIs
GROQ_API_KEY=your_groq_key
GOOGLE_API_KEY=your_gemini_key

# Neo4j Database
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# System
LOG_LEVEL=INFO
```

### **Step 4: Run the Service**
```bash
uvicorn main:app --reload --port 8000
# ✅ Service runs on http://localhost:8000
# 📚 Swagger Docs: http://localhost:8000/docs
```

---

## 📚 API Endpoints

### **Matching & Analysis**
```bash
POST /match-jobs         # Upload PDF resume and get ranked job matches
POST /generate-roadmap   # Generate personalized learning path for a target job
```

### **Job Management (Graph Injection)**
```bash
POST /create-job         # Inject new industry requirements into the Knowledge Graph
GET  /jobs               # List all jobs and their semantic skill nodes
GET  /job/{job_id}       # Retrieve specific job requirements
```

### **System & Diagnostics**
```bash
GET  /health             # Check API and Neo4j connection status
POST /reset-db           # Wipe Neo4j Graph (Use with caution)
```

---

## 🧠 Core Architecture: Autonomous Agents

SkillBridge AI operates using a **Decentralized Multi-Agent Model**:

1.  **Extraction Agent**: Uses LLMs (Llama 3.1) to parse unstructured PDF text into canonicalized skill sets.
2.  **Knowledge Graph Agent**: Injects skills into Neo4j and establishes `REQUIRES` vs `KNOWS` relationships.
3.  **Similarity Agent**: Executes Jaccard Similarity and Weighted Graph-Matching to calculate compatibility scores.
4.  **Retrieval (RAG) Agent**: Crawls for learning resources (YouTube, GitHub, Docs) based on identified skill gaps.
5.  **Planning Agent**: Orchestrates the final roadmap, sequencing steps by difficulty and prerequisites.

---

## 🔗 Backend Integration

This service acts as the **AI brain** for the [Node.js Backend](https://github.com/Rahul-8283/skillbridge-ai-backend). The Node.js server communicates with this FastAPI service via HTTP requests to handle heavy-duty AI computations.

**Example Matching Flow:**
1. Node.js receives Resume PDF -> Forwards to FastAPI `/match-jobs`.
2. FastAPI returns `matchScore` and `missingSkills`.
3. Node.js persists results to MongoDB and notifies the user.

---

## 🎨 Frontend Integration

The user-facing application is built using React and Tailwind CSS. It communicates with the Node.js backend to display AI-generated insights, job matches, and career roadmaps.

**Repository:** [SkillBridge AI Frontend](https://github.com/Rahul-8283/skillbridge-ai-frontend)

---

## 🧪 Testing
Run the automated test suite to verify connectivity and logic:
```bash
python test_api.py
```

---

## 📝 Scripts
- `main.py`: Main FastAPI application.
- `test_api.py`: Script to test major endpoints autonomously.

---

## 🐛 Common Issues
| Issue | Solution |
|-------|----------|
| Neo4j Connection Timeout | Ensure `NEO4J_URI` uses `neo4j+s://` for AuraDB. |
| LLM Rate Limits | Groq has free-tier limits; the service implements retry logic. |
| PDF Parsing Errors | Ensure the PDF is not encrypted or image-only (requires OCR). |

---

## 🏁 Conclusion
The SkillBridge AI Service transforms raw professional data into actionable insights through graph intelligence and autonomous agents. 🚀
riven workflow.

---
**Built for the Future of Work.** 🚀
