from fastapi import FastAPI, Request, HTTPException
from tools.ticket_tools import (
    get_ticket_details,
    acknowledge_and_move_to_inprogress,
    add_ticket_comment
)

app = FastAPI(title="Jira MCP Remote Server")


# Health check
@app.get("/")
def root():
    return {"status": "Jira MCP Server Running"}


# Single MCP execution endpoint
@app.post("/execute")
async def execute(request: Request):
    try:
        body = await request.json()
        print("INCOMING REQUEST:", body)

        tool_name = body.get("tool")
        parameters = body.get("parameters", {})

        if not tool_name:
            return {"error": "No tool provided"}

        if tool_name == "get_ticket":
            return get_ticket_details(parameters.get("issue_key"))

        elif tool_name == "add_comment":
            return add_ticket_comment(
                parameters.get("issue_key"),
                parameters.get("comment")
            )

        elif tool_name == "acknowledge_ticket":
            return acknowledge_and_move_to_inprogress(
                parameters.get("issue_key")
            )

        else:
            return {"error": f"Unknown tool: {tool_name}"}

    except Exception as e:
        print("SERVER ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))