# Production Checklist for GenAI Systems

Use this before deploying any GenAI template to production.

---

## Security
- [ ] API keys stored in environment variables — never hardcoded or in git
- [ ] `.env` added to `.gitignore`
- [ ] Input validation — max token limits enforced
- [ ] PII detection before sending user data to external APIs
- [ ] Rate limiting on all public endpoints
- [ ] Authentication on API endpoints (JWT / API key)

## Reliability
- [ ] Fallback handling when LLM API is unavailable (circuit breaker)
- [ ] Retry logic with exponential backoff for API failures
- [ ] Timeout set on all LLM calls (recommended: 30s)
- [ ] Graceful degradation — what happens if vector store is down?

## Quality
- [ ] Evaluation suite run on your specific domain data
- [ ] Hallucination testing with adversarial prompts
- [ ] Faithfulness score > 0.75 on your test set before going live
- [ ] Human review of 50+ sample outputs before launch

## Observability
- [ ] Every LLM call logged: timestamp, latency, token usage, cost
- [ ] Error rate monitoring (LLM API errors, retrieval failures)
- [ ] Alerting on score degradation (faithfulness drops below threshold)
- [ ] Cost tracking — daily spend alerts configured

## Performance
- [ ] Embedding index pre-built — not on first request
- [ ] Response caching for repeated questions
- [ ] Async endpoints for long-running LLM calls
- [ ] Load tested at expected concurrent user volume

## Compliance (Enterprise)
- [ ] Data residency requirements met (which region is LLM API in?)
- [ ] PII / sensitive data not stored in vector DB without encryption
- [ ] Audit log of all queries and responses retained per policy
- [ ] AI governance framework documented for stakeholders

---

## Common Production Failure Modes

| Failure | Prevention |
|---|---|
| Hallucination at scale | Faithfulness evaluation + grounding prompts |
| Cost overrun | Token limits + budget alerts |
| Slow responses | Async + caching + streaming |
| Context window overflow | Chunk size limits + summarisation |
| Prompt injection | Input sanitisation + system prompt hardening |
| Stale embeddings | Re-index on document updates |
