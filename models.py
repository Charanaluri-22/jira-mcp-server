from pydantic import BaseModel


class TicketRequest(BaseModel):
    issue_key: str


class CommentRequest(BaseModel):
    issue_key: str
    comment: str