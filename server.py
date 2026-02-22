from fastapi import FastAPI,Request
import json
from models import TicketRequest, CommentRequest
from tools.ticket_tools import (
    get_ticket_details,
    acknowledge_and_move_to_inprogress,
    add_ticket_comment
)

app = FastAPI(title="Jira MCP Server")


@app.get("/")
def root():
    return {"message": "Jira MCP Server is running"}


# TOOL 1: Get full ticket details
@app.post("/tools/get_ticket")
def get_ticket_tool(request: TicketRequest):
    return get_ticket_details(request.issue_key)


# TOOL 2: Add comment
@app.post("/tools/add_comment")
def add_comment_tool(request: CommentRequest):
    response = add_ticket_comment(request.issue_key, request.comment)
    return {
        "message": "Comment added successfully",
        "jira_response": response
    }


# TOOL 3: Acknowledge + Move Open → In Progress
@app.post("/tools/acknowledge")
def acknowledge_tool(request: TicketRequest):
    return acknowledge_and_move_to_inprogress(request.issue_key)

@app.post("/webhook/jira")
async def jira_webhook(request: Request):
    """
    Jira webhook listener:
    Triggered when a ticket is created
    """

    payload = await request.json()

    print("\n===== JIRA WEBHOOK RECEIVED =====")
    print(json.dumps(payload, indent=2))
    print("=================================\n")

    # Extract issue key safely
    issue = payload.get("issue", {})
    issue_key = issue.get("key")

    if not issue_key:
        return {"status": "ignored", "reason": "No issue key found"}

    print(f"New Ticket Created: {issue_key}")

    # Call your existing MCP tool
    result = acknowledge_and_move_to_inprogress(issue_key)

    return {
        "status": "processed",
        "issue_key": issue_key,
        "acknowledgement_result": result
    }