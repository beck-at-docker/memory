# Contextual Insight Retrieval System

A sophisticated system designed to replace flat-file memory storage with intelligent, context-aware insight retrieval for therapeutic conversations. Instead of information overload, it provides conversational continuity by surfacing relevant insights based on conversation topics.

## 🎯 Core Problem Solved

Your current system creates information dumps instead of natural conversation flow. This system provides:
- **Topic-triggered access** - Relevant insights surface when specific people/topics are mentioned
- **Temporal intelligence** - Recent insights weighted more heavily, but bedrock truths preserved
- **Growth trajectory tracking** - Focus on transformation rather than static facts
- **Layered information** - Progressive disclosure from surface → mid → deep layers
- **Strategy effectiveness** - Working solutions prioritized over theoretical ones

## 🏗️ System Architecture

### Core Components

1. **`insight_system_simple.py`** - Main retrieval system (no ML dependencies)
2. **`insight_retrieval_system.py`** - Full system with ML capabilities
3. **`data_migration.py`** - Migrates existing conversation files
4. **`conversational_interface.py`** - Natural conversation flow manager
5. **`deploy.py`** - Production deployment script

### Key Features

- **Semantic Triggers**: Automatically detect mentions of A, N, X, trauma responses
- **Crisis Anchors**: Immediate access to grounding insights during overwhelming moments
- **Effectiveness Tracking**: Prioritizes strategies that actually worked
- **Growth Progression**: Tracks evolution from "could I be so lucky?" → "his word is enough"

## 🚀 Quick Start

### 1. Deploy the System
```bash
python3 deploy.py
```

### 2. Basic Usage
```python
from insight_system_simple import SimpleContextualInsightRetrieval

# Initialize
system = SimpleContextualInsightRetrieval("insights.db")

# Retrieve insights
insights = system.retrieve_contextual_insights("I'm worried about trusting A")

# Surface layer (immediate, actionable)
for insight in insights["surface"]:
    print(f"[{insight.insight_type.upper()}] {insight.content}")
```

### 3. Example Outputs

**Input**: "I'm worried about trusting A"
```
[ANCHOR] A is trustworthy. His word is enough. This is bedrock truth.
[STRATEGY] Taking trauma responses to therapy protects relationship with A
```

**Input**: "N is being difficult about boundaries"  
```
[STRATEGY] Boundaries with N are love, not cruelty. Hold the line with love instead of fear.
```

**Input**: "I'm hearing X's voice again"
```
[ANCHOR] X's voice creates inadequacy-scanning. Recognize it as X, not truth.
```

## 🎭 Entity-Specific Triggers

### A (Trust & Relationship)
- **Triggers**: "trust", "A", "relationship", "his word"
- **Surfaces**: Trust anchors, relationship strategies, breakthrough moments
- **Crisis Anchor**: "A is trustworthy. His word is enough."

### N (Parenting & Boundaries)  
- **Triggers**: "N", "boundaries", "parenting", "school", "hygiene"
- **Surfaces**: Boundary strategies, effective parenting approaches
- **Key Strategy**: "Hold the line with love instead of fear"

### X (Trauma & Recovery)
- **Triggers**: "X", "voice", "trauma", "inadequacy", "scanning"
- **Surfaces**: Recognition strategies, healing approaches
- **Core Insight**: "X's voice creates inadequacy-scanning. Recognize it as X, not truth."

### Trauma Responses
- **Triggers**: "activation", "triggered", "nervous system", "shutdown"
- **Surfaces**: Regulation strategies, therapeutic approaches
- **Strategy**: "Taking trauma responses to therapy protects relationship with A"

## 📊 Layered Information Architecture

### Surface Layer (3-5 insights)
- Crisis anchors and bedrock truths
- Recent breakthroughs (last 30 days)  
- High-effectiveness strategies (>0.7 score)
- Currently relevant context

### Mid Layer (5-8 insights)
- Supporting context and background
- Recent developments (last 90 days)
- Moderate-effectiveness strategies
- Related patterns and themes

### Deep Layer (Comprehensive)
- Historical patterns and comprehensive background
- Lower-effectiveness or outdated strategies
- Complete conversation context
- Archived insights and old patterns

## ⏰ Temporal Intelligence

### Recent Priority (Last 30 days)
- Full weight (1.0)
- Automatically surfaces in conversations
- Represents current growth edge

### Historical Context (30+ days ago)  
- Exponential decay weighting
- Preserved for deeper context
- Available in mid/deep layers

### Bedrock Truths (Timeless)
- Maintain relevance regardless of age
- "A is trustworthy. His word is enough."
- "X's voice creates inadequacy-scanning"
- Core therapeutic insights

## 🔄 Growth Trajectory Tracking

### Progression Markers
- **Early**: "Could I be so lucky?"
- **Middle**: "Terrifying but possible"  
- **Recent**: "Yes, his word is enough"
- **Current**: "We are finding our own way together"

### Insight Evolution
- **Foundational**: Core patterns that remain true
- **Evolved**: Updated understanding that builds on earlier insights
- **Superseded**: Old insights replaced by better understanding

## 🚨 Crisis Mode

### Automatic Detection
System detects crisis language:
- "crisis", "emergency", "panic", "overwhelmed" 
- "falling apart", "can't handle", "too much"

### Crisis Response
Immediately surfaces:
- All anchor-type insights
- Highest effectiveness strategies (>0.8)
- Bedrock truths for grounding
- No progressive disclosure - everything accessible

### Example Crisis Output
```
[CRISIS ANCHORS - Hold onto these:]
• A is trustworthy. His word is enough. This is bedrock truth.
• X's voice creates inadequacy-scanning. Recognize it as X, not truth.  
• Taking trauma responses to therapy protects relationship with A
```

## 📈 Strategy Effectiveness Tracking

### Scoring System (0.0 - 1.0)
- **1.0**: Crisis anchors and proven bedrock truths
- **0.8+**: Consistently effective strategies
- **0.6+**: Generally helpful approaches
- **0.4-**: Mixed results or situational effectiveness
- **<0.4**: Ineffective or abandoned approaches

### Effectiveness Indicators
**Positive**: "worked", "effective", "helped", "breakthrough", "success", "able to"
**Negative**: "failed", "couldn't", "didn't work", "backfired", "made worse"  
**Experimental**: "trying", "testing", "attempting", "exploring"

## 🔄 Data Migration from Existing Files

### Automatic Processing
```bash
# Migrate all conversation files
python3 data_migration.py
```

### What Gets Extracted
- **Breakthrough moments** - "shifted something fundamental"
- **Crisis anchors** - Statements marked for remembering  
- **Effective strategies** - Approaches that worked
- **Entity relationships** - A, N, X interaction patterns
- **Growth progression** - Evolution of understanding

### File Processing
- Processes files like `8-19-25`, `7-28-25`, etc.
- Extracts insights from Human/Claude dialogue
- Identifies entities, themes, and insight types
- Calculates effectiveness scores automatically

## 🎯 Success Metrics

The system succeeds when:

✅ **Natural Integration**: Mentioning "A" automatically surfaces trust work without "Remembering..." dumps

✅ **Crisis Support**: Overwhelming moments immediately surface relevant anchoring insights

✅ **Conversational Continuity**: Discussions build meaningfully on previous breakthroughs

✅ **Growth Focus**: System prioritizes transformation narrative over historical facts

✅ **Relevant Context**: Surfaces what's most useful for current situation, not everything

## 🛠️ Advanced Usage

### Custom Insights
```python
# Add new insights manually
system.add_insight(Insight(
    content="New breakthrough understanding",
    entities={"A"},
    themes={"trust", "growth"},
    insight_type="breakthrough",
    effectiveness_score=0.9
))
```

### Deeper Context Access
```python
# Get mid-layer insights
mid_insights = system.retrieve_contextual_insights(input_text, max_insights=15)["mid"]

# Get comprehensive deep context  
deep_insights = system.retrieve_contextual_insights(input_text, max_insights=50)["deep"]
```

### Conversational Integration
```python
from conversational_interface import InsightAPI

api = InsightAPI()
response = api.chat("I'm worried about trusting A")

if response["insights"]:
    print("Relevant context:")
    print(response["insights"])
    
    # Natural conversation continues with context awareness
```

## 📋 File Structure

```
├── insight_system_simple.py      # Core system (no ML deps)
├── insight_retrieval_system.py   # Full system with ML
├── data_migration.py             # Conversation file processor
├── conversational_interface.py   # Natural flow manager
├── deploy.py                     # Production setup
├── test_system.py               # Test suite
├── requirements.txt             # Dependencies
├── usage_examples.md           # Integration examples
└── README.md                   # This file
```

## 🔧 Configuration

### Adjust Triggers
Edit `semantic_triggers` in the system initialization to customize entity detection:

```python
triggers = {
    "A": SemanticTrigger(
        entity="A",
        keywords={"trust", "relationship", "trustworthy", "his word"},
        max_surface_insights=3
    )
}
```

### Modify Layers
Adjust `surface_limit`, `mid_limit` in `LayeredArchitecture` class for different insight counts.

### Effectiveness Tuning
Modify `assess_strategy_effectiveness()` markers to match your specific language patterns.

## 🎨 Integration Philosophy

This system is designed to feel like talking to someone who:
- **Knows your story** without needing to start from scratch
- **Remembers what matters** without overwhelming detail
- **Surfaces relevant context** naturally in conversation
- **Provides anchoring** during difficult moments
- **Tracks your growth** and celebrates progress

The goal is conversational continuity that enhances therapeutic work rather than replacing it.

---

*Built for transforming information overload into meaningful conversational support.*