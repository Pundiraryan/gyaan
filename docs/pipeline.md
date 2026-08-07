# GYAAN Data and AI Pipeline

## Ingestion

1. Collect raw content from sources.
   - RSS feeds
   - Public APIs (Twitter/X, Reddit, Hacker News, GitHub)
   - Playwright web scrapers for sites without APIs
   - Research and blog RSS
2. Normalize metadata and text.
3. Store raw content and metadata.

## Cleaning and deduplication

1. Normalize titles, URLs, and publication timestamps.
2. Remove duplicates by canonical URL and semantic fingerprint.
3. Detect language and filter to supported languages.
4. Tag articles with interest categories using a lightweight classifier.

## Ranking

1. Score by educational value, technical depth, and relevance.
2. Rank by novelty, future relevance, and long-term impact.
3. Choose top 5–10 insights per user segment each day.

## Deep analysis

For each curated insight:
- one-sentence summary
- plain-English translation
- who/what/when/where/why
- why it matters
- concept extraction
- concept explorer pages
- first-principles chains
- timeline / historical context
- expert perspectives
- contrarian perspective
- future predictions
- career relevance
- knowledge graph generation

## Learn Anything

1. Receive topic query and selected depth.
2. Determine prerequisite knowledge.
3. Build concept tree and knowledge graph.
4. Generate explanations at requested depth.
5. Provide recursive follow-up "why" chains.
6. Store learning state for adaptation.

## Cost optimization

- Cache embeddings and AI outputs.
- Reuse existing concept explanations across content.
- Keep deep analysis bounded to top daily insights.
- Prefer small open-source models for pre-processing and summarization.
- Use stronger models only for final presentation and personalization.
