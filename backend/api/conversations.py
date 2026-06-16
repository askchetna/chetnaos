"""Conversation CRUD — persistent chat storage."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.conversation_store import get_conversation_store

router = APIRouter()
_store = get_conversation_store()


class NewConversationRequest(BaseModel):
    title: str = "New conversation"


class ActiveConversationRequest(BaseModel):
    conversation_id: str


@router.get("/api/conversations")
async def list_conversations():
    active = _store.get_active()
    return {
        "conversations": _store.list_conversations(),
        "active_id": active["id"] if active else None,
    }


@router.post("/api/conversations")
async def create_conversation(payload: NewConversationRequest | None = None):
    title = (payload.title if payload else "New conversation") or "New conversation"
    conv = _store.create(title=title)
    return {"conversation": conv}


@router.get("/api/conversations/active")
async def get_active_conversation():
    conv = _store.get_active()
    if not conv:
        conv = _store.create()
    return {"conversation": conv}


@router.get("/api/conversations/{conv_id}")
async def get_conversation(conv_id: str):
    conv = _store.get(conv_id)
    if not conv:
        raise HTTPException(404, "Conversation not found")
    return {"conversation": conv}


@router.post("/api/conversations/active")
async def set_active_conversation(payload: ActiveConversationRequest):
    conv = _store.set_active(payload.conversation_id)
    if not conv:
        raise HTTPException(404, "Conversation not found")
    return {"conversation": conv}


@router.delete("/api/conversations/{conv_id}")
async def delete_conversation(conv_id: str):
    if not _store.delete(conv_id):
        raise HTTPException(404, "Conversation not found")
    active = _store.get_active()
    return {"ok": True, "active_id": active["id"] if active else None}
