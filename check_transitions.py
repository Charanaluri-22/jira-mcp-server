"""
Utility to check available transitions for a Jira ticket
"""

import sys
import json
from jira_client import get_transitions


def show_transitions(issue_key: str):
    """
    Fetch and display all available transitions for a ticket
    """
    print(f"\n🔍 Checking available transitions for {issue_key}...\n")
    
    try:
        response = get_transitions(issue_key)
        transitions = response.get("transitions", [])
        
        if not transitions:
            print(f"❌ No transitions available for {issue_key}")
            return
        
        print(f"✓ Found {len(transitions)} available transition(s):\n")
        print("-" * 60)
        
        for i, transition in enumerate(transitions, 1):
            transition_id = transition.get("id")
            transition_name = transition.get("name")
            to_status = transition.get("to", {}).get("name")
            
            print(f"\n{i}. {transition_name}")
            print(f"   ID: {transition_id}")
            print(f"   To Status: {to_status}")
        
        print("\n" + "-" * 60)
        print(f"\nTo transition, use one of these IDs in the transition_issue() function")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    issue_key = sys.argv[1] if len(sys.argv) > 1 else "MSCSM-3"
    show_transitions(issue_key)
