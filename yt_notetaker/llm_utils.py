from typing import List, Optional

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from .prompts import (
    PLAYLIST_NOTE_TAKER_SYSTEM,
    SINGLE_VIDEO_NOTE_TAKER_SYSTEM,
    JSON_SCHEMA_INSTRUCTIONS,
)
from .schemas import OutlineResponse


def _get_llm(model: str, api_key: Optional[str]) -> ChatOpenAI:
    return ChatOpenAI(model=model, temperature=0, api_key=api_key)


def outline_for_text(title: str, text: str, *, model: str, api_key: Optional[str], playlist_mode: bool) -> OutlineResponse:
    system = SystemMessage(content=(PLAYLIST_NOTE_TAKER_SYSTEM if playlist_mode else SINGLE_VIDEO_NOTE_TAKER_SYSTEM))
    human = HumanMessage(content=(
        f"Title: {title}\n\nTranscript (plaintext):\n" + text[:15000] + "\n\n" + JSON_SCHEMA_INSTRUCTIONS
    ))
    llm = _get_llm(model, api_key)
    response = llm.invoke([system, human])
    content = response.content if hasattr(response, "content") else str(response)
    if content.strip().startswith("```"):
        content = content.strip().strip("`")
        if content.lstrip().lower().startswith("json"):
            content = content.lstrip()[4:]
        content = content.strip()
    import json
    data = json.loads(content)
    return OutlineResponse.model_validate(data)


def merge_outlines(title: str, outlines: List[OutlineResponse], *, model: str, api_key: Optional[str], playlist_mode: bool) -> OutlineResponse:
    system = SystemMessage(content=(
        "You are a master note merger. Merge multiple JSON note outlines into one coherent outline. "
        "Preserve the original order of topics as much as possible and avoid duplication. "
        "Return the same JSON schema with consolidated sections."
    ))
    import json
    outlines_json = json.dumps([o.model_dump() for o in outlines])
    human = HumanMessage(content=(
        f"Title: {title}\n\nOutlines (JSON array):\n{outlines_json}\n\n" + JSON_SCHEMA_INSTRUCTIONS
    ))
    llm = _get_llm(model, api_key)
    response = llm.invoke([system, human])
    content = response.content if hasattr(response, "content") else str(response)
    if content.strip().startswith("```"):
        content = content.strip().strip("`")
        if content.lstrip().lower().startswith("json"):
            content = content.lstrip()[4:]
        content = content.strip()
    data = json.loads(content)
    return OutlineResponse.model_validate(data)


