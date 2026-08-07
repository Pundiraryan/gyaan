# GYAAN Architecture

## Overview

GYAAN is composed of four layers:

1. Data ingestion and cleanup
2. Knowledge representation and retrieval
3. Deep analysis and personalization
4. User experience and presentation

## 1. Data ingestion

### Sources
- X/Twitter API
- LinkedIn public content and feeds
- Reddit subreddits
- Hacker News
- GitHub releases / blog posts
- Product Hunt
- RSS feeds
- Research blogs and arXiv

### Ingestion pipeline
- Worker-based collection using Playwright + API fetchers
- Normalize metadata and content structure
- Store raw items for audit/debug
- Deduplicate by normalized headline / canonical URL / semantic hash
- Assign topics and interest tags using lightweight classifiers

## 2. Knowledge representation

### Data model
- `articles` / `insights`
- `concepts`
- `knowledge_graph_nodes`
- `knowledge_graph_edges`
- `user_profiles`
- `learning_sessions`

### Vector search
- Use Qdrant for semantic retrieval of concepts, articles, and follow-up prompts.
- Keep vector store small by indexing only curated insights and extracted concepts.
- Cache embeddings to reduce AI costs.

## 3. Analysis pipeline

### Article deep dive
For each selected insight:
- one-sentence summary
- plain-English translation
- event narrative
- impact analysis
- concept extraction
- concept explorer content
- first-principles breakdown
- historical context
- expert simulations
- contrarian view
- predictions
- career relevance
- knowledge graph generation

### Recursive learning
- Build `why` chains by generating explanation trees for each concept.
- Store prerequisite sequences to support progressive learning.

## 4. Personalization

### Memory and learning state
- Track topics learned, expertise level, interests, gaps, preferred style.
- Use a lightweight user model to adapt future explanations.
- Recommend follow-ups based on learning history and strength areas.

### Free-tier optimization
- Limit daily deep analysis to 5–10 insights.
- Use embeddings and cached prompts for repeat queries.
- Prefer open-source models and local APIs where possible.
- Use incremental generation only for larger drafts.

## Deployment and scaling

### Backend
- Containerize FastAPI service with Docker
- Support horizontal scaling with stateless API workers
- Use managed PostgreSQL and Redis for state and caching
- Qdrant can run self-hosted or via managed service

### Jobs
- Run ingestion and ranking jobs separately from API workers
- Use Celery or APScheduler for scheduled tasks
- Allow worker scaling independently of the API

## UX architecture

### Tab 1: Daily Insights
- curated insight cards
- insight detail page with deep dive sections
- actionable learning links and concept exploration

### Tab 2: Learn Anything
- query entry with depth level selector
- prerequisite graph and knowledge tree
- follow-up questions and recursive why flow

## Key design principles

- Depth first, not breadth first
- Quality over volume
- Educational scaffolding over raw news
- Reuse retrieval to save costs
- Keep AI prompts and outputs interpretable
- Build an extensible knowledge graph
