# Swasth AI – Medical AI Backend (Proof of Work)

Swasth AI is a **backend-focused medical AI system** built to understand how real-world LLM applications are designed, optimized, and made safer beyond prompt engineering.

This project is **not a demo chatbot**. It focuses on backend system design, Retrieval-Augmented Generation (RAG), streaming correctness, memory architecture, and performance tradeoffs.

---

## What this project demonstrates

* Backend system design for LLM-powered applications
* Retrieval-Augmented Generation (RAG) using a vector database (Qdrant)
* Streaming responses (SSE) with correct token handling
* Short-term vs long-term memory separation (Redis + vector DB)
* Tool-based architecture (non-agentic, explicit tool usage)
* Safety constraints for sensitive domains (medical)
* Latency optimization (reduced response time from ~20s to ~6s)

---

## High-level architecture

```
User
 ↓
FastAPI Backend (Python)
 ├─ Prompt construction & safety rules
 ├─ Streaming orchestration (SSE)
 ├─ Tool routing (explicit, user-triggered)
 ├─ Short-term memory (Redis – hot state)
 └─ Long-term semantic memory (Qdrant – cold state)
 ↓
Ollama (Local LLM)
```

External services:

* Qdrant → vector search for medical knowledge & long-term memory
* Redis → current chat context, caching, working memory (future implementation)
* Optional Geo service → nearby hospital search (tool-based)

---

## Core components

### 1. LLM

* **Runtime**: Ollama (local)
* **Model**: phi3:mini
* **Why local**: control, observability, lower latency, no API abstraction

---

### 2. Retrieval-Augmented Generation (RAG)

* Medical documents are embedded using `nomic-embed-text`
* Stored in **Qdrant** as vectors with metadata
* At query time:

  * Relevant medical context is retrieved
  * Injected into the prompt explicitly
  * The LLM never answers without grounded context

This avoids prompt-only hallucinations and keeps answers explainable.

---

### 3. Memory architecture

The system intentionally separates memory by **time horizon and purpose**:

#### Short-term memory (Redis) 

future implementation

* Recent chat messages
* Streaming state
* Cached RAG results
* TTL-based, disposable

#### Long-term memory (Qdrant)

* Summarized past conversations
* Explicit "remember this" facts
* Semantic recall across sessions

This avoids dumping raw chat logs into vector storage and keeps memory meaningful.

---

### 4. Streaming responses

* Implemented using **Server-Sent Events (SSE)**
* Correct handling of subword tokens (no artificial spacing)
* Backend streams tokens; frontend appends them incrementally

This provides real-time feedback without breaking tokenizer semantics.

---

### 5. Tool-based design (non-agentic)

The system supports **explicit tools**, not autonomous agents.

Example tool:

* Nearby hospital search (via OpenStreetMap through an external service)

Design principles:

* Tools are deterministic
* LLM decides *when* to use a tool, not *how*
* User consent is required
* Results are explained, never instructed

This keeps the system controllable and safe.

---

### 6. Safety constraints

Because this is a medical domain prototype:

* No diagnosis is provided
* No emergency instructions are given
* Risk-aware language is enforced
* The assistant recommends consulting licensed professionals when appropriate

Safety is treated as a **backend responsibility**, not a UI afterthought.

---

## Performance work

Initial naive RAG + memory design resulted in:

* ~15–20 seconds response time

Optimizations applied:

* Prompt size control
* Limiting memory injection
* Smarter RAG gating
* Streaming to improve perceived latency

Result:

* ~6 seconds end-to-end response time
* Immediate token streaming for better UX

---

## Tech stack

* **Backend**: Python, FastAPI
* **LLM runtime**: Ollama
* **Vector DB**: Qdrant
* **Cache / Memory**: Redis (planned)
* **Streaming**: SSE
* **Embeddings**: nomic-embed-text

---

## Why this project exists

This project was built to move beyond:

* tutorial-driven AI projects
* prompt-only chatbots
* opaque "agent" abstractions

The goal was to understand:

* how LLM systems actually fail
* how memory should be designed
* how to reduce hallucinations
* how to reason about latency and correctness

---

## Status

* Backend complete and functional
* RAG working
* Streaming stable
* Memory architecture in place
* Tool integration supported

Ongoing work:

* Better memory summarization
* Evaluation harness
* Further prompt compression

---

## Disclaimer

This project is for **educational and engineering exploration purposes only**.
It is **not** a production medical system and does not provide medical advice.

---

## Author

**Om Anand**
GitHub: [https://github.com/Om-anand-0](https://github.com/Om-anand-0)
LinkedIn: [https://www.linkedin.com/in/omanand10/](https://www.linkedin.com/in/omanand10/)
