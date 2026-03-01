import json
from jira_client import (
    get_ticket,
    add_comment,
    get_transitions,
    transition_issue
)


def extract_description(adf):
    """Extract plain text from Jira ADF description"""
    if not adf or "content" not in adf:
        return None

    text_parts = []

    for block in adf.get("content", []):
        if "content" in block:
            for item in block["content"]:
                if item.get("type") == "text":
                    text_parts.append(item.get("text", ""))

    return " ".join(text_parts)


def get_ticket_details(issue_key: str):
    """Get full structured ticket details + print raw JSON"""
    ticket = get_ticket(issue_key)

    fields = ticket.get("fields", {})

    return {
        "key": ticket.get("key"),
        "summary": fields.get("summary"),
        "description": extract_description(fields.get("description")),
        "status": fields.get("status", {}).get("name"),
        "priority": fields.get("priority", {}).get("name"),
        "assignee": (
            fields.get("assignee", {}).get("displayName")
            if fields.get("assignee")
            else None
        ),
        "reporter": fields.get("reporter", {}).get("displayName"),
        "issue_type": fields.get("issuetype", {}).get("name"),
        "labels": fields.get("labels"),
        "components": [c["name"] for c in fields.get("components", [])],
        "created": fields.get("created"),
        "updated": fields.get("updated"),
    }


def find_progress_transition(transitions):
    """
    Smart transition finder for workflows like:
    - Start work
    - Begin progress
    - Work in progress
    """
    priority_keywords = ["start", "progress", "work", "in progress"]

    # First pass: strong match
    for t in transitions:
        name = t["name"].lower()
        to_status = t["to"]["name"].lower()

        if any(k in name for k in priority_keywords) or any(
            k in to_status for k in priority_keywords
        ):
            return t["id"]

    return None


def acknowledge_and_move_to_inprogress(issue_key: str):
    """
    MCP Tool:
    1. Reads ticket
    2. Adds acknowledgment comment
    3. Moves ticket to Work in Progress (using workflow transitions)
    """

    print(f"\nProcessing ticket: {issue_key}")

    # Step 1: Get ticket
    ticket = get_ticket(issue_key)
    fields = ticket.get("fields", {})
    current_status = fields.get("status", {}).get("name", "").lower()

    print("CURRENT STATUS:", current_status)

    # Step 2: Skip if already in progress
    if "progress" in current_status:
        return {
            "message": "Ticket already in progress state",
            "current_status": current_status,
        }

    # Step 3: Add acknowledgment comment
    comment_text = "Ticket acknowledged by MCP Server. Investigation started."
    comment_response = add_comment(issue_key, comment_text)

    print("COMMENT RESPONSE:", comment_response)

    # Step 4: Get available transitions
    transitions_data = get_transitions(issue_key)
    transitions = transitions_data.get("transitions", [])

    print("\nAVAILABLE TRANSITIONS:")
    for t in transitions:
        print(f"- {t['name']} (ID: {t['id']}) -> {t['to']['name']}")

    # Step 5: Find correct transition (dynamic)
    transition_id = find_progress_transition(transitions)

    if not transition_id:
        return {
            "error": "No valid progress transition found",
            "current_status": current_status,
            "available_transitions": [
                {
                    "name": t["name"],
                    "id": t["id"],
                    "to": t["to"]["name"],
                }
                for t in transitions
            ],
        }

    # Step 6: Perform transition
    print(f"\nEXECUTING TRANSITION ID: {transition_id}")
    status_code = transition_issue(issue_key, transition_id)

    print("TRANSITION STATUS CODE:", status_code)

    return {
        "message": "Ticket acknowledged and moved to progress state",
        "issue_key": issue_key,
        "transition_id": transition_id,
        "jira_api_status": status_code,
    }


def add_ticket_comment(issue_key: str, comment: str):
    """Simple MCP tool to add comments to Jira ticket"""
    response = add_comment(issue_key, comment)
    print("ADD COMMENT RESPONSE:", response)
    return response