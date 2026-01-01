# Local LLM Quick Reference

## One-Time Setup

```bash
cd ~/Documents/private

# Make setup script executable
chmod +x setup_llm_quick.sh

# Run setup (installs everything)
./setup_llm_quick.sh
```

## Daily Usage

### Extract Insights from Conversations
```bash
python3 extract_conversation_insights_llm.py
# Choose: Y for LLM, n for pattern matching
```

### Test LLM Connection
```bash
python3 llm_client.py
```

### See Keyword vs LLM Comparison
```bash
python3 demo_llm_comparison.py
```

### Use in Code
```python
from llm_client import LocalLlama

# Initialize
llm = LocalLlama()

# Extract insights
insights = llm.extract_insights_from_conversation(text)

# Score relevance
score = llm.semantic_match_score(query, insight)

# Summarize
summary = llm.summarize_insights(insight_list)
```

### Use Enhanced Retrieval
```python
from insight_system_llm import LLMEnhancedInsightRetrieval

# Initialize with LLM ranking
system = LLMEnhancedInsightRetrieval(
    db_path="memory_data/personal_insights.db",
    use_llm_ranking=True
)

# Query (auto-ranked by LLM)
results = system.retrieve_contextual_insights("your query")

# Get summary
summary = system.get_llm_summary("your query")
```

## Docker Model Runner Commands

```bash
# Check status
docker model status

# List models
docker model ls

# Pull Llama 3.3
docker model pull ai/llama3.3

# Remove model
docker model rm ai/llama3.3

# Run quick test
docker model run ai/llama3.3 "test"
```

## Troubleshooting

### Model Runner not responding
```bash
docker desktop enable model-runner --tcp 12434
```

### First query very slow
**Normal.** Model loads on first query (30-60 sec). Subsequent queries: 2-5 sec.

### Connection refused
Enable TCP in Docker Desktop:  
`Settings → Features → Enable "host-side TCP support"`

### Model not found
```bash
docker model pull ai/llama3.3
```

## Performance Tips

- **Real-time queries:** Use keyword matching (fast)
- **Batch processing:** Use LLM (accurate)
- **First query:** Expect 30-60 sec delay
- **Subsequent queries:** 2-5 sec each

## Resource Requirements

- **Disk:** ~4.5GB (model + dependencies)
- **RAM:** ~6GB while running
- **GPU:** Optional but recommended

## Files

```
llm_client.py                        # LLM interface
extract_conversation_insights_llm.py # LLM extraction
insight_system_llm.py                # Enhanced retrieval
demo_llm_comparison.py               # See differences
setup_llm_quick.sh                   # Quick setup
README_LLM.md                        # Full docs
```

## Privacy

✓ 100% local processing  
✓ No API calls  
✓ No data leaves your machine  
✓ No quotas or costs  

---

**Quick help:** `cat README_LLM.md`  
**Full docs:** `cat IMPLEMENTATION_SUMMARY.md`
