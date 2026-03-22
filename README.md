# FastAPI Financial Document Management with Semantic Analysis

This project is a FastAPI-based backend system for managing financial documents with semantic search using Retrieval-Augmented Generation (RAG).

## Features

- User Authentication
- Role-Based Access Control
- Document Upload & Management
- Metadata Search
- Semantic Search using Embeddings
- ChromaDB
- Reranking for improved search results

## Tech Stack

- FastAPI
- SQLAlchemy
- SQLite
- Sentence Transformers
- ChromaDB

## API Endpoints

### Auth
- POST /auth/register
- POST /auth/login

### Documents
- POST /documents/upload
- GET /documents
- DELETE /documents/{id}
- GET /documents/search

### RAG
- POST /rag/index-document
- POST /rag/search

### RBAC
- POST /roles/create
- POST /users/assign-role
