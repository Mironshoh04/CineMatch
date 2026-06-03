from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ..schemas.ai import ChatRequest
from ..services.llm_service import stream_chat

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/chat")
async def chat(body: ChatRequest):
    return StreamingResponse(
        stream_chat(body.message, body.history),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
