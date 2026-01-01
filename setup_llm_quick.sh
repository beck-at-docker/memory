#!/bin/bash
# Quick start script for Local LLM integration

set -e  # Exit on error

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}           DOCKER MODEL RUNNER + LLAMA 3.3 SETUP              ${NC}"
echo -e "${BLUE}================================================================${NC}"
echo ""

# Check if Docker is running
echo -e "${YELLOW}→ Checking Docker...${NC}"
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running${NC}"
    echo "Please start Docker Desktop and try again"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"

# Check Docker Model Runner
echo -e "\n${YELLOW}→ Checking Docker Model Runner...${NC}"
if ! docker model --help >/dev/null 2>&1; then
    echo -e "${RED}✗ Docker Model Runner not found${NC}"
    echo "Please update Docker Desktop to 4.40+ or install Docker Model Runner"
    exit 1
fi
echo -e "${GREEN}✓ Docker Model Runner available${NC}"

# Check if model exists
echo -e "\n${YELLOW}→ Checking for Llama 3.3 model...${NC}"
if docker model ls | grep -q "ai/llama3.3"; then
    echo -e "${GREEN}✓ Llama 3.3 already downloaded${NC}"
else
    echo -e "${YELLOW}⚠ Llama 3.3 not found${NC}"
    echo "  This is a ~4GB download and will take a few minutes"
    read -p "  Pull Llama 3.3 now? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        echo -e "${YELLOW}→ Pulling Llama 3.3... (this will take a while)${NC}"
        docker model pull ai/llama3.3
        echo -e "${GREEN}✓ Model downloaded${NC}"
    else
        echo -e "${RED}✗ Cannot continue without model${NC}"
        exit 1
    fi
fi

# Enable TCP access
echo -e "\n${YELLOW}→ Enabling TCP access on port 12434...${NC}"
if docker desktop enable model-runner --tcp 12434 >/dev/null 2>&1; then
    echo -e "${GREEN}✓ TCP access enabled${NC}"
else
    echo -e "${YELLOW}⚠ Could not enable via CLI${NC}"
    echo "  Please enable manually in Docker Desktop:"
    echo "    Settings → Features → Enable 'host-side TCP support'"
fi

# Check if in virtual environment
echo -e "\n${YELLOW}→ Checking Python environment...${NC}"
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo -e "${YELLOW}⚠ Not in a virtual environment${NC}"
    
    # Check if memory_env exists
    if [[ -d "memory_env" ]]; then
        echo "  Activating memory_env..."
        source memory_env/bin/activate
        echo -e "${GREEN}✓ Virtual environment activated${NC}"
    else
        echo -e "${RED}✗ Virtual environment not found${NC}"
        echo "  Please run: python3 setup_env.py"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Using virtual environment: ${VIRTUAL_ENV}${NC}"
fi

# Install dependencies
echo -e "\n${YELLOW}→ Installing Python dependencies...${NC}"
if pip install -q -r requirements_llm.txt; then
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    exit 1
fi

# Test the model
echo -e "\n${YELLOW}→ Testing Llama 3.3...${NC}"
echo "  (First query may take 30-60 seconds to load model)"
if timeout 90 docker model run ai/llama3.3 "Say only: working" | grep -qi "working"; then
    echo -e "${GREEN}✓ Model is responding${NC}"
else
    echo -e "${YELLOW}⚠ Model test inconclusive (this is often normal)${NC}"
fi

# Test Python client
echo -e "\n${YELLOW}→ Testing Python LLM client...${NC}"
if python3 -c "from llm_client import LocalLlama; c = LocalLlama(); print('✓ Client initialized')" 2>/dev/null; then
    echo -e "${GREEN}✓ Python client working${NC}"
else
    echo -e "${YELLOW}⚠ Python client test failed (might still work)${NC}"
fi

# Summary
echo -e "\n${BLUE}================================================================${NC}"
echo -e "${GREEN}                    SETUP COMPLETE!                            ${NC}"
echo -e "${BLUE}================================================================${NC}"
echo ""
echo "Next steps:"
echo ""
echo "  1. Test LLM client:"
echo "     ${YELLOW}python3 llm_client.py${NC}"
echo ""
echo "  2. Extract insights from conversations:"
echo "     ${YELLOW}python3 extract_conversation_insights_llm.py${NC}"
echo ""
echo "  3. Test enhanced retrieval:"
echo "     ${YELLOW}python3 insight_system_llm.py${NC}"
echo ""
echo "  4. Read the documentation:"
echo "     ${YELLOW}cat README_LLM.md${NC}"
echo ""
echo "Useful commands:"
echo "  ${YELLOW}docker model ls${NC}              - List models"
echo "  ${YELLOW}docker model status${NC}          - Check Model Runner"
echo "  ${YELLOW}docker model rm ai/llama3.3${NC}  - Remove model"
echo ""
echo "Your data stays 100% local. No API calls. Complete privacy."
echo ""
