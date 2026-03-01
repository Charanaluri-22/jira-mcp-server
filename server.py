import json
import os

import uvicorn
from fastapi import FastAPI, Request
from mcp.server.fastmcp import FastMCP

from tools.ticket_tools import (
    acknowledge_and_move_to_inprogress,
    add_ticket_comment,
    get_ticket_details,
)

mcp = FastMCP(
    "jira-mcp-server",
    # When mounted at /mcp, expose MCP directly at /mcp/ (not /mcp/mcp).
    streamable_http_path="/",
)
mcp_app = mcp.streamable_http_app()


@mcp.tool(
    name="get_ticket",
    description="Get structured Jira issue details by issue key.",
)
def get_ticket_tool(issue_key: str) -> dict:
    return get_ticket_details(issue_key)


@mcp.tool(
    name="add_comment",
    description="Add a comment to a Jira issue.",
)
def add_comment_tool(issue_key: str, comment: str) -> dict:
    response = add_ticket_comment(issue_key, comment)
    return {
        "message": "Comment added successfully",
        "jira_response": response,
    }


@mcp.tool(
    name="acknowledge",
    description="Acknowledge a Jira issue and move it into progress state.",
)
def acknowledge_tool(issue_key: str) -> dict:
    return acknowledge_and_move_to_inprogress(issue_key)


app = FastAPI(title="Jira MCP Server", lifespan=mcp_app.lifespan)
app.mount("/mcp", mcp_app)


@app.get("/")
def root() -> dict:
    return {
        "message": "Jira MCP Server is running",
        "mcp_endpoint": "/mcp",
        "tools": ["get_ticket", "add_comment", "acknowledge"],
    }


@app.post("/execute")
async def execute(request: Request) -> dict:
    """
    Backward-compatible execution route for existing HTTP clients.
    """
    body = await request.json()
    tool_name = body.get("tool")
    parameters = body.get("parameters", {})

    if tool_name == "get_ticket":
        return get_ticket_tool(parameters.get("issue_key"))

    if tool_name == "add_comment":
        return add_comment_tool(
            parameters.get("issue_key"),
            parameters.get("comment"),
        )

    if tool_name in {"acknowledge", "acknowledge_ticket"}:
        return acknowledge_tool(parameters.get("issue_key"))

    return {"error": f"Unknown tool: {tool_name}"}


@app.post("/webhook/jira")
async def jira_webhook(request: Request) -> dict:
    """
    Jira webhook listener for new issue events.
    """
    payload = await request.json()

    print("\n===== JIRA WEBHOOK RECEIVED =====")
    print(json.dumps(payload, indent=2))
    print("=================================\n")

    issue = payload.get("issue", {})
    issue_key = issue.get("key")

    if not issue_key:
        return {"status": "ignored", "reason": "No issue key found"}

    print(f"New Ticket Created: {issue_key}")
    result = acknowledge_and_move_to_inprogress(issue_key)

    return {
        "status": "processed",
        "issue_key": issue_key,
        "acknowledgement_result": result,
    }


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "streamable-http").lower()

    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        uvicorn.run(
            "server:app",
            host="0.0.0.0",
            port=int(os.getenv("PORT", "8000")),
        )
