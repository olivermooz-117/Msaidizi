from google import genai
from google.genai import types
from backend.app.config import settings

_client = None


def get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Return embeddings (list of vectors). Uses gemini-embedding-2."""
    if not texts:
        return []
    client = get_client()
    result = client.models.embed_content(
        model=settings.EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=settings.EMBEDDING_DIM,
        ),
    )
    return [e.values for e in result.embeddings]


def embed_query(text: str) -> list[float]:
    client = get_client()
    result = client.models.embed_content(
    model=settings.EMBEDDING_MODEL,
    contents=texts,
    config=types.EmbedContentConfig(
        output_dimensionality=768,
    ),
)
    return result.embeddings[0].values


def generate(system: str, messages: list[dict], tools: list | None = None) -> dict:
    """
    Simple non-streaming generate.
    messages = [{"role": "user"|"model", "content": "..."}]
    Returns {"text": str, "function_calls": list}
    """
    client = get_client()

    contents = []
    for m in messages:
        role = "user" if m["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=m["content"])]))

    config = types.GenerateContentConfig(
        system_instruction=system,
        temperature=0.2,
        max_output_tokens=512,
    )
    if tools:
        config.tools = tools

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=contents,
        config=config,
    )

    text = ""
    function_calls = []
    if response.candidates:
        for part in response.candidates[0].content.parts:
            if part.text:
                text += part.text
            if part.function_call:
                function_calls.append({
                    "name": part.function_call.name,
                    "args": dict(part.function_call.args) if part.function_call.args else {},
                })

    return {"text": text.strip(), "function_calls": function_calls}
