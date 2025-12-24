# What i am building ?
## A containerized RAG-based chatbot service with automated deployment and self-recovery. 

### Ollama -> Using Ollama for generating response for the prompt
### python -> Using Python for Backend
           #### Libraries Used
                * FastApi  -> for Handling Backend, routing etc.
                * Uvicorn  -> for running backend
                * shutil   -> for advanced file operations
                * os       -> for accessing operating system and directory
                * pydantic -> for validating data 
                * pypdf    -> for ingesting pdfs (used in rag)
                * requests -> for accesing embedder in docker
### Qdrant -> Using Qdrant for Vector Database, for storing and retrival of chat    

# Components
    ## Runtime Services

        * Backend (FastApi)
        * Frontend (Static website for now)
        * ollama (gemma:3b, nomic embedder)
        * Qdrant 
    ## Platform Tools
        * Docker 
        * Jenkins

# CI/CD 
    * Jenkins 
        ## pipline -> checkout(takes github branch), verify docker, build(build apps), run tests, deploy


# Data Flow > 
    ## User -> Backend -> embedder -> ollama -> Backend -> User
    ## Backend <-> Qdrant

# Failure Modes
    1. Service Container Crashes
    2. Application Process crashes
    3. Model latency Spikes
    4. Disk exhaustion due to uploaded documents
    5. CI/CD Pipeline Failure

# Detection & recovery
    1. Container Crashes => Automate the restarting on failure
    2. Application Process crashes => Crash → restart container, Repeated crash → rollback to previous image
    3. Model latency Spikes => Use metrics to keep watching for meteric to spike -> use caching to give replies
    4. Disk exhaustion due to uploaded documents => Disk usage monitoring, setup alerts before disk full
    5. CI/CD Pipeline Failure => investigate logs -> fix -> rerun 


