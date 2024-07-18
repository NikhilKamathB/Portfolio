from pydantic import BaseModel


class ChatResponse(BaseModel):
    success: bool
    message: str
    description: str 