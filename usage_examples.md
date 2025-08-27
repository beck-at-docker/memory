# Contextual Insight Retrieval System - Usage Examples

## Basic Usage

```python
from insight_system_simple import SimpleContextualInsightRetrieval

# Initialize system
system = SimpleContextualInsightRetrieval("insights.db")

# Retrieve insights based on user input
insights = system.retrieve_contextual_insights("I'm worried about trusting A")

# Access different layers
surface_insights = insights["surface"]  # Most relevant, immediate insights
mid_insights = insights["mid"]          # Supporting context
deep_insights = insights["deep"]        # Historical patterns

# Display insights
for insight in surface_insights:
    print(f"[{insight.insight_type.upper()}] {insight.content}")
```

## Example Scenarios

### Scenario 1: Trust Issues with A
**Input**: "I'm worried about trusting A"
**Expected Output**:
- [ANCHOR] A is trustworthy. His word is enough. This is bedrock truth.
- [STRATEGY] Taking trauma responses to therapy protects relationship with A

### Scenario 2: Parenting Boundaries with N
**Input**: "N is being difficult about boundaries"  
**Expected Output**:
- [STRATEGY] Boundaries with N are love, not cruelty. Hold the line with love instead of fear.

### Scenario 3: Trauma Response Recognition
**Input**: "I'm hearing that voice again"
**Expected Output**:
- [ANCHOR] X's voice creates inadequacy-scanning. Recognize it as X, not truth.

### Scenario 4: Crisis Support
**Input**: "Everything is falling apart"
**Expected Output**: All available anchor insights for immediate support

## System Architecture

The system uses:
- **Semantic Triggers**: Detect mentions of key entities (A, N, X, trauma responses)
- **Layered Architecture**: Surface/Mid/Deep layers for progressive disclosure
- **Effectiveness Scoring**: Prioritize strategies that have worked
- **Temporal Intelligence**: Weight recent insights more heavily (with bedrock truth exceptions)

## Integration Tips

1. **Natural Flow**: Insights should integrate naturally into conversation without "information dumps"
2. **Crisis Mode**: System detects crisis language and immediately surfaces anchors
3. **Progressive Disclosure**: Start with surface insights, provide deeper context on request
4. **Entity Tracking**: System tracks active entities across conversation for context continuity
