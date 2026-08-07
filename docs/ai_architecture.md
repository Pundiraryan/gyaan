# GYAAN AI Architecture

## Goals

- Deliver deep understanding, not shallow summaries.
- Maximize free-tier usage through caching and open-source models.
- Keep explanations reusable and composable.
- Support progressive depth and recursive "why" exploration.

## Model strategy

### Primary preference
- Open-source and low-cost LLMs for pre-processing, concept extraction, and summarization.
- Providers like OpenRouter, Hugging Face, Qwen, or local LLMs when available.

### Secondary preference
- Managed models for high-quality final presentation and personalization when necessary.
- Use smaller models for quick responses and larger models only when the value justifies cost.

## Prompt design

- Standardize prompts for core sections: summary, plain English, concept extraction, historical context.
- Reuse prompt templates across content types.
- Cache outputs by prompt fingerprint + content fingerprint.

## Retrieval and memory

- Store extracted concepts and deep analysis outputs in vector store.
- Use semantic retrieval to answer follow-up questions and fill knowledge gaps.
- Track user learning state and adapt explanations to their preferred depth and style.

## Cost optimization

- Only deep-analyze the top 5–10 curated insights per day.
- Cache embeddings and text generation outputs.
- Share concept explanations across related insights.
- Rate-limit AI usage per user and use async batch generation when possible.
