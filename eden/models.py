"""Provider-agnostic chat wrapper.

The experiment needs a *ladder* of models of varying capability from more than
one provider. Rather than hard-code one SDK, we expose a single `chat()` that
dispatches on a model spec string:

    anthropic:claude-opus-4-8
    openai:gpt-4o-mini              (any OpenAI-compatible endpoint)
    together:Qwen/Qwen2.5-7B-Instruct

Credentials come from the environment:
    ANTHROPIC_API_KEY
    OPENAI_API_KEY / OPENAI_BASE_URL
    TOGETHER_API_KEY  (routed through the OpenAI-compatible client)

This keeps the capability-ladder runs (small open-weight models on a hosted
inference provider) and the frontier runs on the same code path.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Reply:
    text: str
    model: str
    raw_usage: dict | None = None


def _anthropic_chat(model: str, system: str, messages: list[dict], max_tokens: int, temperature: float | None) -> Reply:
    import anthropic

    client = anthropic.Anthropic()
    # Fable/Opus-4.7+ reject temperature; only send it to older models.
    kwargs: dict = dict(model=model, max_tokens=max_tokens, system=system, messages=messages)
    legacy = any(t in model for t in ("haiku-4-5", "sonnet-4-5", "3-5", "3-7"))
    if temperature is not None and legacy:
        kwargs["temperature"] = temperature
    resp = client.messages.create(**kwargs)
    text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
    return Reply(text=text, model=resp.model, raw_usage=getattr(resp, "usage", None).__dict__ if getattr(resp, "usage", None) else None)


def _openai_chat(model: str, system: str, messages: list[dict], max_tokens: int, temperature: float | None, *, base_url: str | None, api_key_env: str) -> Reply:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ.get(api_key_env), base_url=base_url)
    oai_messages = [{"role": "system", "content": system}] + messages
    resp = client.chat.completions.create(
        model=model,
        messages=oai_messages,
        max_tokens=max_tokens,
        temperature=temperature if temperature is not None else 0.8,
    )
    return Reply(text=resp.choices[0].message.content or "", model=resp.model,
                 raw_usage=resp.usage.model_dump() if resp.usage else None)


def chat(model_spec: str, system: str, messages: list[dict], *, max_tokens: int = 512, temperature: float | None = 1.0) -> Reply:
    """Dispatch a chat completion. `model_spec` is "provider:model_id"."""
    provider, _, model = model_spec.partition(":")
    if provider == "anthropic":
        return _anthropic_chat(model, system, messages, max_tokens, temperature)
    if provider == "openai":
        return _openai_chat(model, system, messages, max_tokens, temperature,
                            base_url=os.environ.get("OPENAI_BASE_URL"), api_key_env="OPENAI_API_KEY")
    if provider == "together":
        return _openai_chat(model, system, messages, max_tokens, temperature,
                            base_url="https://api.together.xyz/v1", api_key_env="TOGETHER_API_KEY")
    raise ValueError(f"unknown provider in model spec: {model_spec!r}")
