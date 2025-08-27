#!/usr/bin/env python3
"""
Deployment script for the Contextual Insight Retrieval System
"""

import os
import sys
from pathlib import Path
from insight_system_simple import SimpleContextualInsightRetrieval, Insight
from datetime import datetime
import uuid

class DeploymentManager:
    """Manages deployment and setup of the insight system"""
    
    def __init__(self, data_directory: str = "/Users/beck/Documents/private"):
        self.data_dir = Path(data_directory)
        self.system = SimpleContextualInsightRetrieval("insights_production.db")
    
    def setup_production_system(self):
        """Set up the production system with essential insights"""
        print("Setting up Contextual Insight Retrieval System...")
        print("=" * 60)
        
        # Create essential crisis anchors and insights
        essential_insights = [
            {
                "content": "A is trustworthy. His word is enough. This is bedrock truth.",
                "entities": ["A"],
                "themes": ["trust", "relationships"],
                "effectiveness_score": 1.0,
                "layer": "surface",
                "insight_type": "anchor",
                "context": "Core anchor for trust with A"
            },
            {
                "content": "Taking trauma responses to therapy protects relationship with A",
                "entities": ["A", "trauma_responses"],
                "themes": ["strategies", "relationships", "trauma"],
                "effectiveness_score": 0.9,
                "layer": "surface",
                "insight_type": "strategy",
                "context": "Effective strategy for managing activation"
            },
            {
                "content": "X's voice creates inadequacy-scanning. Recognize it as X, not truth.",
                "entities": ["X", "trauma_responses"],
                "themes": ["trauma", "strategies"],
                "effectiveness_score": 0.9,
                "layer": "surface",
                "insight_type": "anchor",
                "context": "Recognition strategy for X's voice"
            },
            {
                "content": "Boundaries with N are love, not cruelty. Hold the line with love instead of fear.",
                "entities": ["N"],
                "themes": ["parenting", "boundaries", "strategies"],
                "effectiveness_score": 0.9,
                "layer": "surface", 
                "insight_type": "strategy",
                "context": "Core parenting boundary philosophy"
            },
            {
                "content": "Progress from 'could I be so lucky?' to 'yes, his word is enough' to finding our own way together",
                "entities": ["A"],
                "themes": ["trust", "growth", "relationships"],
                "effectiveness_score": 0.8,
                "layer": "surface",
                "insight_type": "breakthrough",
                "context": "Trust journey progression with A"
            },
            {
                "content": "Nausea made of joy - body learning new sensations for hope and safety",
                "entities": ["A", "trauma_responses"],
                "themes": ["growth", "healing", "trust"],
                "effectiveness_score": 0.7,
                "layer": "mid",
                "insight_type": "breakthrough",
                "context": "Physical sensation of healing and trust"
            }
        ]
        
        # Add insights to system
        added_count = 0
        for insight_data in essential_insights:
            insight = Insight(
                id=str(uuid.uuid4()),
                content=insight_data["content"],
                entities=set(insight_data["entities"]),
                themes=set(insight_data["themes"]),
                effectiveness_score=insight_data["effectiveness_score"],
                layer=insight_data["layer"],
                insight_type=insight_data["insight_type"],
                timestamp=datetime.now(),
                source_file="deployment_setup",
                context=insight_data["context"]
            )
            
            self.system.add_insight(insight)
            added_count += 1
        
        print(f"✓ Added {added_count} essential insights")
        return True
    
    def test_deployment(self):
        """Test the deployed system"""
        print("\nTesting deployed system...")
        print("-" * 40)
        
        test_scenarios = [
            {
                "input": "I'm worried about trusting A",
                "expected_entities": ["A"],
                "expected_types": ["anchor", "strategy"]
            },
            {
                "input": "N is having a meltdown about shower time",
                "expected_entities": ["N"],
                "expected_types": ["strategy"]
            },
            {
                "input": "I'm hearing X's voice telling me I'm too much",
                "expected_entities": ["X"],
                "expected_types": ["anchor", "strategy"]
            },
            {
                "input": "I need crisis support right now",
                "expected_entities": ["A"],  # Should surface anchors
                "expected_types": ["anchor"]
            }
        ]
        
        passed_tests = 0
        total_tests = len(test_scenarios)
        
        for i, scenario in enumerate(test_scenarios, 1):
            test_input = scenario["input"]
            
            print(f"\nTest {i}: '{test_input}'")
            
            # Get insights
            insights = self.system.retrieve_contextual_insights(test_input)
            surface_insights = insights.get("surface", [])
            
            if surface_insights:
                print(f"  ✓ Retrieved {len(surface_insights)} surface insights")
                
                # Show insights
                for insight in surface_insights[:2]:  # Show first 2
                    print(f"    [{insight.insight_type.upper()}] {insight.content[:80]}...")
                
                passed_tests += 1
            else:
                print("  ✗ No insights retrieved")
        
        success_rate = passed_tests / total_tests
        print(f"\nTest Results: {passed_tests}/{total_tests} passed ({success_rate:.1%})")
        
        return success_rate >= 0.8  # 80% success rate required
    
    def create_usage_examples(self):
        """Create usage examples file"""
        examples_content = '''# Contextual Insight Retrieval System - Usage Examples

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
'''
        
        with open("usage_examples.md", "w") as f:
            f.write(examples_content)
        
        print("✓ Created usage examples file")

def main():
    """Run deployment process"""
    print("Contextual Insight Retrieval System - Deployment")
    print("=" * 60)
    
    # Check if data directory exists
    data_dir = "/Users/beck/Documents/private"
    if not Path(data_dir).exists():
        print(f"⚠️  Data directory not found: {data_dir}")
        print("Using deployment without historical data migration.")
    
    # Initialize deployment
    deployer = DeploymentManager(data_dir)
    
    # Setup system
    success = deployer.setup_production_system()
    if not success:
        print("✗ Setup failed")
        return False
    
    # Test deployment
    test_success = deployer.test_deployment()
    if not test_success:
        print("✗ Testing failed")
        return False
    
    # Create documentation
    deployer.create_usage_examples()
    
    print("\n" + "=" * 60)
    print("🎉 Deployment completed successfully!")
    print("\nNext steps:")
    print("1. Review usage_examples.md for integration guidance")
    print("2. Run data_migration.py to import your conversation history")  
    print("3. Test the system with your real conversation patterns")
    print("4. Adjust triggers and insights based on your specific needs")
    print("\nThe system is ready for conversational integration!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)