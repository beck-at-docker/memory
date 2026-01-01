#!/bin/bash
# Comprehensive test script for LLM integration

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}              TESTING LLM INTEGRATION                         ${NC}"
echo -e "${BLUE}================================================================${NC}"
echo ""

cd ~/Documents/private

# Test 1: Check Docker
echo -e "${YELLOW}Test 1: Checking Docker...${NC}"
if docker info >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker is running${NC}"
else
    echo -e "${RED}✗ Docker is not running${NC}"
    exit 1
fi

# Test 2: Check Docker Model Runner
echo -e "\n${YELLOW}Test 2: Checking Docker Model Runner...${NC}"
if docker model --help >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker Model Runner available${NC}"
else
    echo -e "${RED}✗ Docker Model Runner not found${NC}"
    exit 1
fi

# Test 3: Check for Llama 3.3
echo -e "\n${YELLOW}Test 3: Checking for Llama 3.3...${NC}"
if docker model ls 2>/dev/null | grep -q "ai/llama3.3"; then
    echo -e "${GREEN}✓ Llama 3.3 model found${NC}"
else
    echo -e "${RED}✗ Llama 3.3 not found${NC}"
    echo "Please run: docker model pull ai/llama3.3"
    exit 1
fi

# Test 4: Activate virtual environment
echo -e "\n${YELLOW}Test 4: Checking Python environment...${NC}"
if [[ -d "memory_env" ]]; then
    source memory_env/bin/activate
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
else
    echo -e "${RED}✗ memory_env not found${NC}"
    exit 1
fi

# Test 5: Check dependencies
echo -e "\n${YELLOW}Test 5: Installing dependencies...${NC}"
pip install -q -r requirements_llm.txt
echo -e "${GREEN}✓ Dependencies ready${NC}"

# Test 6: Test LLM client
echo -e "\n${YELLOW}Test 6: Testing LLM client (this takes 30-60 sec first time)...${NC}"
python3 llm_client.py

# Test 7: Test comparison demo
echo -e "\n${YELLOW}Test 7: Running comparison demo...${NC}"
python3 demo_llm_comparison.py

echo -e "\n${BLUE}================================================================${NC}"
echo -e "${GREEN}                    ALL TESTS COMPLETE                        ${NC}"
echo -e "${BLUE}================================================================${NC}"
