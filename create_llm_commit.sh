#!/bin/bash
# Create git commit for LLM integration work

cd ~/Documents/private

echo "Adding LLM integration files to git..."

# Add new LLM files
git add \
  llm_client.py \
  extract_conversation_insights_llm.py \
  insight_system_llm.py \
  requirements_llm.txt \
  setup_llm.py \
  setup_llm_quick.sh \
  demo_llm_comparison.py \
  test_llm_simple.py \
  test_llm_integration.sh \
  README_LLM.md \
  IMPLEMENTATION_SUMMARY.md \
  TESTING_INSTRUCTIONS.md \
  LLM_QUICK_REFERENCE.md

echo "Files staged. Creating commit..."

# Commit with the detailed message
git commit -F COMMIT_MESSAGE_LLM.txt

echo ""
echo "✓ Commit created!"
echo ""
echo "Review your commit:"
echo "  git log -1"
echo "  git show"
echo ""
echo "Push when ready:"
echo "  git push origin main"
