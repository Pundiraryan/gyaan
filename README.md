# GYAAN

Understand Anything. Deeply.

## Product Vision

GYAAN is a knowledge-first learning platform that turns signals from modern technical content into expert-level understanding. It is designed to help users move from "what happened" to "why it matters" and "what I need to know next."

## Core capabilities

- Daily Insights: curated, deeply analyzed, top 5–10 insights every day.
- Learn Anything: explain any topic at beginner, student, engineer, or expert depth.
- Concept explorer with recursive "why" and prerequisite detection.
- Personalized memory, learning history, and follow-up guided paths.

## High-level architecture

### Frontend
- Flutter mobile/web app
- Riverpod for state management
- GoRouter for navigation
- Material 3 UI

### Backend
- Python + FastAPI
- PostgreSQL for relational storage
- Redis for caching and rate limiting
- Qdrant for vector search and concept retrieval
- APScheduler / Celery for ingestion and pipeline jobs

### AI pipeline
- Source collection: RSS, APIs, Playwright / scraper workers
- Cleaning & deduplication
- Classification and importance ranking
- Concept extraction and knowledge graph generation
- Deep article analysis and recursive explanation generation
- Personalization and memory adaptation

## Why this stack

- Python/FastAPI gives rapid backend development with strong async and ML integration.
- PostgreSQL is mature, scalable, and cost-efficient for user profiles, content metadata, and history.
- Qdrant supports vector search and semantic retrieval with open-source compatibility.
- Flutter builds cross-platform mobile and web UI from a single codebase.
- Redis enables low-latency caching and protects free-tier usage with efficient reuse.

## Next steps

1. Implement backend API patterns for content ingestion and analysis.
2. Build core UI flows: Daily Insights, Topic Search, Article Deep Dive.
3. Design data schema for content, concepts, knowledge graphs, and user memory.
4. Wire up an open-source embedding + LLM provider strategy with prompt caching.
5. Add scheduler and ingestion worker prototypes.

## Project layout

- `frontend/` - Flutter app
- `backend/` - FastAPI service
- `docs/` - architecture and design docs
- `scripts/` - future deployment and maintenance scripts

## Goals for this phase

- Create a minimal viable backend API for content retrieval and topic explanations.
- Scaffold a Flutter app with the two primary tabs.
- Capture architecture decisions in documentation.
- Optimize the design for maintainability, cost control, and free-tier AI usage.
