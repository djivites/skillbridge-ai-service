# 🚀 SkillBridge AI
### *Bridging the Gap Between Talent and Industry with Autonomous Multi-Agent Workflows.*

---

## 🛠️ Technology Stack

### **Frontend**
![React](https://img.shields.io/badge/React-Latest-blue?logo=react) 
![Vite](https://img.shields.io/badge/Vite-Latest-brightgreen?logo=vite) 
![Zustand](https://img.shields.io/badge/Zustand-State%20Management-brown?logo=javascript) 
![Axios](https://img.shields.io/badge/Axios-HTTP%20Client-purple?logo=axios)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-Styling-06B6D4?logo=tailwindcss)
![Deployment](https://img.shields.io/badge/Deployment-Vercel-000000?logo=vercel)

### **Backend**
![Node.js](https://img.shields.io/badge/Node.js-Latest-339933?logo=node.js) 
![Express](https://img.shields.io/badge/Express-Web%20Framework-000000?logo=express) 
![MongoDB](https://img.shields.io/badge/MongoDB-Database-47A248?logo=mongodb) 
![Mongoose](https://img.shields.io/badge/Mongoose-ODM-880000?logo=mongoose)
![Redis](https://img.shields.io/badge/Redis-Cache-DC382D?logo=redis)
![JWT](https://img.shields.io/badge/JWT-Authentication-000000?logo=auth0)
![Multer](https://img.shields.io/badge/Multer-File%20Upload-FF6B6B?logo=npm)
![Deployment](https://img.shields.io/badge/Deployment-Render-46E3B7?logo=render)

### **AI Service**
![Python](https://img.shields.io/badge/Python-3.10+-3776ab?logo=python) 
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi) 
![Neo4j](https://img.shields.io/badge/Neo4j-Knowledge%20Graph-0081C2?logo=neo4j)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Storage-FFF000?logo=pinecone)
![LLMs](https://img.shields.io/badge/LLMs-Gemini%20%2F%20Groq-4285F4?logo=google)

---

SkillBridge AI is a state-of-the-art multi-agent system designed to revolutionize career guidance and recruitment. It autonomously handles the entire lifecycle of professional growth—from analyzing complex resumes to generating personalized, time-sensitive learning roadmaps to bridge real-world skill gaps.

---

## 📌 Problem Statement
The modern job market suffers from a massive "Disconnected Data" problem:
* **Students & Job Seekers:** Don't know how "job-ready" they actually are for specific roles.
* **Overwhelming Information:** Learning resources are scattered (YouTube, Wikis, GitHub), making it impossible to build a structured path.
* **Manual Mismatch:** Traditional job boards use keyword matching, ignoring the deep semantic relationships between skills.

---

## 💡 Solution
SkillBridge AI solves this end-to-end by treating the career-matching process as an **Autonomous Enterprise Workflow**. It doesn't just "search" for jobs; it **calculates** the professional distance between a candidate and a role, then **autonomously constructs and executes** a plan to bridge that gap.

---

## 🧠 Architecture Overview
The system follows a linear, yet deeply intelligent pipeline:
1. **Intelligent Extraction:** Parsing unstructured resumes into structured skill sets.
2. **Graph Injection:** Mapping skills into a Neo4j Knowledge Graph to understand "Prerequisite" relationships.
3. **Semantic Matching:** Comparing User Skill Graphs against Job Requirement Graphs.
4. **Gap Analysis:** Pinpointing exactly what's missing.
5. **RAG-Powered Discovery:** Fetching specialized resources for missing skills.
6. **Dynamic Orchestration:** Generating roadmaps and time estimates via multi-LLM workflows.

---

## 🤖 Agentic AI Design (Category: Autonomous Enterprise Workflows)
SkillBridge AI is built on a **Multi-Agent Orchestration** model. Each stage of the pipeline is handled by a specialized agent that acts independently but contributes to the global state.

### 🕵️ The Agent Roster:
* **Extraction Agent (NLP/LLM):** Autonomously parses PDFs, identifies semantic meaning, and filters noise from resumes.
* **Knowledge Graph Agent (Neo4j):** Manages the "Memory" of the industry. It builds relationships (`REQUIRES`, `KNOWS`) and ensures skill hierarchy.
* **Matching Agent (Similarity Engine):** Executes complex graph-matching algorithms to determine compatibility scores without human bias.
* **Retrieval Agent (RAG):** An autonomous researcher. It queries YouTube, GitHub, and Wikipedia APIs to find high-signal learning content.
* **Understanding Agent:** Synthesizes raw data into human-legible skill summaries.
* **Planning Agent:** The "Architect." It sequences missing skills into a logical learning order based on graph prerequisites.
* **Time Estimation Agent:** Uses predictive LLM modeling to calculate "Time-to-Completion" based on a user's daily study capacity.

### ⚙️ Why it’s "Agentic":
* **Autonomous Decision Making:** The system decides which resources are relevant and how to structure a roadmap without manual curation.
* **Self-Correcting Pipeline:** If a skill is missing from the Knowledge Graph, the system triggers an "Inference Agent" to predict its prerequisites based on LLM training data.
* **Auditable Execution:** Every step of the workflow—from skill extraction to final roadmap—is logged and verifiable within the graph database.

---

## 🔄 Workflow Automation
The entire process is a **Zero-Manual-Intervention** loop:
1. **Input:** User uploads a PDF Resume and specifies a Target Job.
2. **Autonomous Processing:** The Agents collaborate behind the scenes to extract, link, match, and research.
3. **Output:** A complete "Suitability Report" and "Personalized Roadmap" delivered in seconds.

---

## 📊 Features
* **Resume Intelligence:** High-accuracy parsing of professional experience.
* **Knowledge Graph Engine:** Visualizes career paths as interconnected skill nodes.
* **Weighted Similarity Scoring:** Moves beyond keywords to true capability matching.
* **Native RAG Integration:** Instant access to curated learning materials.
* **Personalized Roadmap Generation:** AI-curated steps to reach "Job Ready" status.
* **Adaptive Time Tracking:** Dynamic estimates based on user availability.

---

## 🧩 Tech Stack
* **Framework:** FastAPI (High-performance Python backend)
* **Knowledge Graph:** Neo4j (Graph Database)
* **Orchestration / LLMs:** Gemini API (Primary) / Groq (High-speed inference)
* **Vector Memory:** ChromaDB (for RAG resource caching)
* **Language:** Python 3.10+

---

## 📦 API Endpoints
* `POST /create-job`: Injects new industry requirements into the Knowledge Graph.
* `POST /match-jobs`: The primary entry point. Uploads a resume and returns ranked matches.
* `POST /generate-roadmap`: Triggers the Planning and Retrieval agents to build a learning path.
* `POST /reset-db`: Diagnostic tool to clear the workspace for fresh trial runs.

---

## 🧪 Example Flow
1. **Upload:** User uploads `software_engineer_resume.pdf`.
2. **Match:** System returns a 85% match for "Backend Developer" but identifies a gap in `Redis` and `Kafka`.
3. **Analyze:** The Matching Agent highlights these gaps.
4. **Generate:** The Planning Agent pulls YouTube tutorials and GitHub docs for Redis/Kafka and generates a 2-week roadmap.

---

## 📈 Evaluation Alignment
**Category: Agentic AI for Autonomous Enterprise Workflows**
* **Multi-Agent Coordination:** Demonstrates seamless collaboration between vector retrieval, graph logic, and LLM reasoning.
* **Autonomy:** Operates from start to finish with "one-click" input.
* **Enterprise Ready:** Scalable architecture using Neo4j and FastAPI ensures it can handle thousands of job/resume nodes efficiently.

---

## 🔮 Future Scope
* **Real-time Skill Tracking:** Integration with browser extensions to track learning progress.
* **Adaptive Pathing:** Adjusting roadmaps mid-way if a user finds a topic easy or difficult.
* **LMS Connect:** Direct "One-Click Enrollment" into Coursera/Udemy/LinkedIn Learning courses.

---

## 🏁 Conclusion
SkillBridge AI is more than a tool; it is an **Autonomous Career Consultant**. By leveraging a multi-agent architecture, it removes the friction and uncertainty from professional development, turning the complex journey from "student" to "professional" into a streamlined, AI-driven workflow.

---
**Built for the Future of Work.** 🚀
