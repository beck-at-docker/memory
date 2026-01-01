# Local LLM Integration - Docker Model Runner + Llama 3.3

## Overview

Your memory system now supports **100% local LLM processing** via Docker Model Runner and Llama 3.3. This means:

- **Zero API calls** to any cloud service (including Anthropic)
- **Complete privacy** - all data stays on your machine
- **No quotas or costs** - run as much as you want
- **Graceful fallback** - if LLM isn't available, falls back to keyword matching

## What's New

### 1. LLM-Powered Insight Extraction

**Before (Pattern Matching):**
```python
# Used regex patterns like:
r"I realized that (.+)"
r"What worked was (.+)"
```

**After (LLM Extraction):**
- Understands natural conversation flow
- Extracts insights without rigid patterns
- Identifies entities, themes, and insight types automatically
- Scores effectiveness based on context

### 2. Semantic Retrieval Ranking

**Before (Keyword Matching):**
```
Query: "Can I trust A?"
Matches: Any insight containing "trust" or "A"
```

**After (Semantic Matching):**
- "Can I trust A?" matches "A is reliable" (no keyword overlap!)
- Ranks by meaning, not just word overlap
- More relevant results in fewer queries

### 3. Insight Summarization

New capability: Ask for a summary of multiple related insights and get a natural language synthesis.

## New Files

```
/Users/beck/Documents/private/
├── llm_client.py                      # Local Llama 3.3 client
├── extract_conversation_insights_llm.py  # LLM-powered extraction
├── insight_system_llm.py              # LLM-enhanced retrieval
├── requirements_llm.txt               # Updated dependencies
├── setup_llm.py                       # Setup script
└── README_LLM.md                      # This file
```

## Setup Instructions

### Quick Start

```bash
# 1. Run the setup script
cd ~/Documents/private
python3 setup_llm.py

# 2. Follow the prompts - it will:
#    - Check Docker installation
#    - Enable Docker Model Runner
#    - Pull Llama 3.3 (~4GB download)
#    - Install Python dependencies
#    - Test the integration
```

### Manual Setup

If you prefer to set up manually:

```bash
# 1. Pull the model
docker model pull ai/llama3.3

# 2. Enable TCP access (port 12434)
docker desktop enable model-runner --tcp 12434

# 3. Install Python dependencies
source memory_env/bin/activate
pip install -r requirements_llm.txt

# 4. Test it
python3 llm_client.py
```

### Verify Setup

```bash
# Check model is available
docker model ls

# Should show:
# MODEL           PARAMETERS  QUANTIZATION  ARCHITECTURE  MODEL ID      CREATED       SIZE
# ai/llama3.3     ...         ...           llama         ...           ...           ...

# Check Model Runner status
docker model status

# Should show:
# Docker Model Runner is running
# Status: llama.cpp: running
```

## Usage

### Extract Insights from Conversations

```bash
# Using LLM (recommended for better accuracy)
python3 extract_conversation_insights_llm.py

# You'll be prompted:
# "Use local Llama 3.3 for extraction? (Y/n):"

# Answer Y for LLM extraction, n for pattern matching
```

**What happens:**
- Reads conversations from `/Users/beck/Documents/private/conversations/`
- Uses Llama 3.3 to extract meaningful insights
- Adds them to your memory database
- Falls back to pattern matching if LLM fails

### Test LLM-Enhanced Retrieval

```bash
# Run the test suite
python3 insight_system_llm.py

# This will:
# 1. Add test insights
# 2. Compare keyword vs LLM ranking
# 3. Show example summaries
```

### Use in Your Code

```python
from insight_system_llm import LLMEnhancedInsightRetrieval

# Initialize with LLM ranking
system = LLMEnhancedInsightRetrieval(
    db_path="memory_data/personal_insights.db",
    use_llm_ranking=True,
    llm_ranking_threshold=5  # Only use LLM if >5 results
)

# Query as normal
results = system.retrieve_contextual_insights("worried about trust")

# Results are automatically re-ranked by semantic relevance

# Get a summary
summary = system.get_llm_summary("worried about trust", max_insights=5)
print(summary)
```

### Integration with Memory API

To enable LLM in your running memory API server, you'll need to update `memory_api.py` to use `LLMEnhancedInsightRetrieval` instead of `SimpleContextualInsightRetrieval`. This is optional - the system works fine without it.

## Performance Expectations

### First Query
- **Cold start:** 20-60 seconds (model loads into memory)
- **Subsequent queries:** 2-5 seconds per LLM call

### Keyword-Only Queries
- **Speed:** <100ms (unchanged)
- **Use when:** Real-time conversation needs

### LLM-Enhanced Queries
- **Speed:** 2-5 seconds
- **Use when:** Batch processing or offline analysis

## Configuration

### Environment Variables

Add to your `.env` or export:

```bash
# Enable/disable LLM features
export USE_LLM=true

# Docker Model Runner endpoint
export LLM_BASE_URL=http://localhost:12434/engines/v1

# Model to use
export LLM_MODEL=ai/llama3.3
```

### Config Updates

Modify `config.py`:

```python
class Config:
    # ... existing config ...
    
    # LLM Settings
    USE_LLM = os.getenv('USE_LLM', 'true').lower() == 'true'
    LLM_BASE_URL = os.getenv('LLM_BASE_URL', 'http://localhost:12434/engines/v1')
    LLM_MODEL = os.getenv('LLM_MODEL', 'ai/llama3.3')
```

## Troubleshooting

### "Docker Model Runner not available"

**Solution:**
```bash
# Check Docker is running
docker info

# Check Model Runner is enabled
docker model status

# Enable TCP access
docker desktop enable model-runner --tcp 12434

# Restart Docker Desktop
```

### "Connection refused" or "Connection timeout"

**Cause:** Model Runner not accessible on port 12434

**Solution:**
```bash
# Option 1: Enable TCP in Docker Desktop GUI
# Settings → Features → Enable "host-side TCP support"

# Option 2: Check if something else is using port 12434
lsof -i :12434

# Option 3: Try different port
export LLM_BASE_URL=http://localhost:8080/engines/v1
```

### "Model not found"

**Solution:**
```bash
# Check what models you have
docker model ls

# Pull Llama 3.3 if not present
docker model pull ai/llama3.3
```

### LLM extraction is very slow

**Cause:** First query loads model into memory

**Solutions:**
1. **Accept it:** First query is slow, subsequent ones are faster
2. **Keep model warm:** Run a test query periodically
3. **Batch process:** Extract from all conversations at once, not one-by-one

### LLM returns no insights

**Check:**
1. Is conversation text substantial? (needs ~50+ words)
2. Check logs: `cat logs/memory_api.log | grep llm`
3. Test manually: `python3 llm_client.py`

**Fallback:** System automatically uses pattern matching if LLM fails

## Comparing Results: LLM vs Keywords

### Example Query: "Can I really trust A?"

**Keyword Matching:**
1. "A is trustworthy. His word is enough." ✓ (contains "A" and "trust")
2. "Trust builds through consistent actions" ✓ (contains "trust")
3. "X's voice creates inadequacy-scanning" ✗ (contains neither)

**LLM Semantic Matching:**
1. "A is trustworthy. His word is enough." ✓✓✓ (directly answers)
2. "Trust builds through consistent actions" ✓✓ (general principle)
3. "Taking trauma responses to therapy protects relationship with A" ✓ (relevant context)

**Result:** LLM finds related insights that keyword matching misses.

## Resource Usage

### Disk Space
- Llama 3.3 model: ~4GB
- Total with all dependencies: ~4.5GB

### Memory (RAM)
- Model loaded: ~4-6GB
- System overhead: ~500MB
- Total: **~5-7GB while running**

### CPU/GPU
- **With GPU:** Fast inference (2-3 sec/query)
- **Without GPU:** Slower but usable (5-10 sec/query)

Docker Model Runner automatically uses GPU if available (Metal on Mac, CUDA on Linux/Windows).

## Privacy & Security

✓ **100% local** - No data leaves your machine  
✓ **No API keys** - No cloud credentials needed  
✓ **No logs sent** - All processing is private  
✓ **No telemetry** - Docker Model Runner doesn't phone home  

Your sensitive personal data never touches external servers.

## Advanced: Other Models

Want to try different models?

```bash
# List available models
docker model ls --remote

# Some options:
docker model pull ai/llama3.2   # Smaller, faster
docker model pull ai/mistral    # Good for code
docker model pull ai/phi4       # Lightweight

# Use in code:
from llm_client import LocalLlama
client = LocalLlama(model="ai/mistral")
```

## Next Steps

1. **Run setup:** `python3 setup_llm.py`
2. **Test extraction:** Extract insights from a conversation file
3. **Compare results:** Run same query with/without LLM ranking
4. **Measure improvement:** Does LLM find better insights for your use case?

## Getting Help

**Check logs:**
```bash
cat logs/memory_api.log | grep -i llm
```

**Test components individually:**
```bash
python3 llm_client.py              # Test LLM connection
python3 insight_system_llm.py      # Test retrieval
docker model status                # Check Model Runner
```

**Common issues:**
- Port 12434 conflicts → Change port in config
- Model too slow → Normal on first query
- Out of memory → Llama 3.3 needs ~6GB RAM

## References

- Docker Model Runner docs: https://docs.docker.com/ai/model-runner/
- Llama 3.3 on Docker Hub: https://hub.docker.com/r/ai/llama3.3
- OpenAI Python SDK: https://github.com/openai/openai-python

---

**Built for complete privacy and local control of your personal data.**
