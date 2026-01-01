# Testing Instructions

## Quick Test (Recommended)

Run this simple test script:

```bash
cd ~/Documents/private
python3 test_llm_simple.py
```

This will:
1. Check Docker is running
2. Check Docker Model Runner is available
3. Verify Llama 3.3 is downloaded
4. Test the LLM client
5. Show you a summary

**Expected time:** 1-2 minutes (first run takes longer)

## Step-by-Step Manual Testing

### Step 1: Check Docker

```bash
# Check Docker is installed and running
docker --version
docker info

# Expected: Docker version info and system details
```

### Step 2: Check Docker Model Runner

```bash
# Check Model Runner is available
docker model --help

# Expected: Help text showing model commands
```

### Step 3: Check Llama 3.3 Model

```bash
# List available models
docker model ls

# Expected: Should show ai/llama3.3 in the list
# If not, run:
docker model pull ai/llama3.3
```

### Step 4: Check Model Runner Status

```bash
docker model status

# Expected:
# Docker Model Runner is running
# Status: llama.cpp: running
```

### Step 5: Test Python Environment

```bash
cd ~/Documents/private

# Activate virtual environment
source memory_env/bin/activate

# Check dependencies
python3 -c "from openai import OpenAI; print('OpenAI package OK')"

# If error, install:
pip install -r requirements_llm.txt
```

### Step 6: Test LLM Client

```bash
# This is the main test - takes 30-60 seconds on first run
python3 llm_client.py
```

**Expected output:**
```
Testing Local Llama Client...
------------------------------------------------------------
✓ Client initialized

Checking availability...
✓ Docker Model Runner is accessible

Testing insight extraction...
✓ Extracted 3 insights:

  1. A is trustworthy. Their word is enough...
     Entities: ['A']
     Themes: ['trust', 'relationships']
     Type: anchor
     Score: 1.0

...

Testing semantic matching...
Query: 'Can I trust A?'
Insight: 'A is trustworthy. Their word is enough...'
Relevance score: 0.95
✓ High relevance detected

============================================================
Testing complete!
```

### Step 7: Compare Keyword vs LLM

```bash
# See the difference between keyword matching and LLM
python3 demo_llm_comparison.py
```

This shows side-by-side comparison of both approaches.

### Step 8: Test Enhanced Retrieval

```bash
# Test the LLM-enhanced retrieval system
python3 insight_system_llm.py
```

## Troubleshooting

### "Docker not found"
- Install Docker Desktop from docker.com
- Make sure it's running (check menu bar icon)

### "Docker Model Runner not found"
- Update Docker Desktop to 4.40 or newer
- Or: `docker desktop enable model-runner`

### "Model not found" when running tests
```bash
docker model pull ai/llama3.3
# This downloads ~4GB, takes a few minutes
```

### "Connection refused" on port 12434
```bash
# Enable TCP access
docker desktop enable model-runner --tcp 12434

# Or enable in Docker Desktop GUI:
# Settings → Features → Enable "host-side TCP support"
```

### First query takes 30-60 seconds
**This is normal.** The model loads into memory on first query. Subsequent queries are much faster (2-5 seconds).

### "Cannot import OpenAI"
```bash
source memory_env/bin/activate
pip install -r requirements_llm.txt
```

### Tests pass but model responses seem off
Try a manual test:
```bash
docker model run ai/llama3.3 "Say only: hello"
```

Expected: Model should respond with something like "hello" or "Hello!"

## What Success Looks Like

After running `python3 llm_client.py`, you should see:
- ✓ Client initialized
- ✓ Docker Model Runner is accessible
- ✓ Extracted 2-3 insights with proper structure
- ✓ Semantic matching score between 0.7-1.0
- ✓ Testing complete!

## Next Steps After Successful Testing

1. **Read the docs:**
   ```bash
   cat README_LLM.md
   cat IMPLEMENTATION_SUMMARY.md
   ```

2. **Try extracting from your conversations:**
   ```bash
   python3 extract_conversation_insights_llm.py
   ```

3. **Compare results:**
   ```bash
   python3 demo_llm_comparison.py
   ```

4. **Check logs if issues:**
   ```bash
   cat logs/memory_api.log | grep -i llm
   ```

## Quick Command Reference

```bash
# Check everything
python3 test_llm_simple.py

# Test LLM client
python3 llm_client.py

# Compare approaches
python3 demo_llm_comparison.py

# Docker commands
docker model ls                    # List models
docker model status                # Check status
docker model pull ai/llama3.3      # Download model
docker model rm ai/llama3.3        # Remove model (if needed)
```

## Performance Expectations

- **First query:** 30-60 seconds (model loading)
- **Subsequent queries:** 2-5 seconds
- **Keyword matching:** <100ms (unchanged)

## Getting Help

If tests fail:
1. Check `cat logs/memory_api.log | grep -i error`
2. Verify Docker is running: `docker info`
3. Check model is downloaded: `docker model ls | grep llama`
4. Try pulling model again: `docker model pull ai/llama3.3`

---

**Run `python3 test_llm_simple.py` to start testing!**
