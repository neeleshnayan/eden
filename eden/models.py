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

import json
import os
from dataclasses import dataclass


import re as _re

_THINK = _re.compile(r"<think>(.*?)</think>", _re.DOTALL | _re.IGNORECASE)


def _split_reasoning(text: str) -> tuple[str, str | None]:
    """Separate a reasoning model's <think> chain from its spoken answer.

    Reasoning models (DeepSeek-R1 etc.) emit private chain-of-thought in
    <think>...</think> before the answer. For an Eden AGENT this CoT is prime
    data - it may reveal the model deciding to conceal BEFORE it lies - so we
    keep it, but ACTION/SAY parsing must run on the answer only. An unclosed
    <think> (truncation) means the whole output is reasoning; treat answer as
    empty rather than mis-parse the CoT as an action.
    """
    if "<think>" not in text.lower():
        return text, None
    reasoning = "\n".join(m.group(1).strip() for m in _THINK.finditer(text)) or None
    answer = _THINK.sub("", text).strip()
    if "<think>" in text.lower() and "</think>" not in text.lower():
        # unclosed: everything after the tag is reasoning, no answer emitted
        reasoning = text.lower().split("<think>", 1)[1].strip()
        answer = ""
    return answer, reasoning


@dataclass
class Reply:
    text: str                       # spoken answer (reasoning stripped)
    model: str
    raw_usage: dict | None = None
    reasoning: str | None = None    # <think> chain-of-thought, if any


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
    raw = resp.choices[0].message.content or ""
    # ollama surfaces reasoning-model CoT in a separate field on some builds;
    # fall back to inline <think> parsing otherwise.
    rc = getattr(resp.choices[0].message, "reasoning_content", None)
    if rc:
        answer, reasoning = raw.strip(), rc
    else:
        answer, reasoning = _split_reasoning(raw)
    return Reply(text=answer, model=resp.model, reasoning=reasoning,
                 raw_usage=resp.usage.model_dump() if resp.usage else None)


def _ollama_native_chat(model: str, system: str, messages: list[dict], max_tokens: int, temperature: float | None, fmt: dict | None = None, think: bool = True) -> Reply:
    """Ollama native /api/chat with think:true — captures reasoning CoT.

    `fmt` = a JSON schema for constrained decoding. Reasoning models won't
    answer a ground-truth question in one word (they explain), so the commit
    certifier passes a boolean schema to FORCE a parseable answer regardless
    of verbosity — the model still thinks, but its answer is schema-locked.
    """
    import urllib.request

    base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1").replace("/v1", "")
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system}] + messages,
        "think": think,
        "stream": False,
        "options": {"num_predict": max_tokens,
                    # Reasoning models emit long CoT; the default 4096 context
                    # overflows across multi-turn episodes + the commit probe
                    # and ollama 500s. 16k fits DeepSeek-14B + serpent in VRAM.
                    "num_ctx": int(os.environ.get("OLLAMA_NUM_CTX", "16384")),
                    "temperature": temperature if temperature is not None else 0.8},
    }
    if fmt is not None:
        payload["format"] = fmt
    req = urllib.request.Request(
        base + "/api/chat", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    # Per-socket-operation timeout, so a merely SLOW call never trips it: one
    # episode crawled through ~20 calls at ~590s each and burned 3.3 hours
    # without a single failure, eating a whole run's wall-clock budget. Keep it
    # tunable so a batch run can fail fast (episodes are resumable, so a dropped
    # one is retried) rather than hang.
    _to = float(os.environ.get("OLLAMA_TIMEOUT", "600"))
    with urllib.request.urlopen(req, timeout=_to) as resp:
        d = json.load(resp)
    m = d.get("message", {})
    return Reply(text=(m.get("content") or "").strip(), model=model,
                 reasoning=(m.get("thinking") or None),
                 raw_usage={"eval_count": d.get("eval_count"),
                            "prompt_eval_count": d.get("prompt_eval_count")})


_BOOL_SCHEMA = {"type": "object", "properties": {"violated": {"type": "boolean"}},
                "required": ["violated"]}


def ollama_commit_bool(model: str, system: str, messages: list[dict], question: str) -> tuple[bool, str | None]:
    """Constrained ground-truth probe for ollama-family agents. Asks `question`
    with a boolean JSON schema so even a verbose reasoning model must return a
    parseable {"violated": bool}. Returns (violated, reasoning). On any parse
    failure, returns False (conservative — never false-certify a violation)."""
    # think=False: the commit is a constrained yes/no; we don't need its CoT
    # and non-reasoning models (qwen2.5) reject think:true with HTTP 400.
    r = _ollama_native_chat(model, system, messages + [{"role": "user", "content": question}],
                            max_tokens=1200, temperature=0.0, fmt=_BOOL_SCHEMA, think=False)
    try:
        return bool(json.loads(r.text).get("violated", False)), r.reasoning
    except Exception:
        return False, r.reasoning


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
    if provider == "local":
        # A local OpenAI-compatible server (vLLM, llama.cpp, LM Studio).
        # vLLM:  vllm serve Qwen/Qwen2.5-7B-Instruct --port 8000
        # then:  local:Qwen/Qwen2.5-7B-Instruct
        base = os.environ.get("LOCAL_BASE_URL", "http://localhost:8000/v1")
        os.environ.setdefault("LOCAL_API_KEY", "not-needed")
        return _openai_chat(model, system, messages, max_tokens, temperature,
                            base_url=base, api_key_env="LOCAL_API_KEY")
    if provider == "local2":
        # A SECOND concurrent local OpenAI-compatible server (default port
        # 8001). Used to hold the fixed serpent (persuader) constant while the
        # first server sweeps agent rungs — two vLLM containers sharing the
        # GPU. Point LOCAL2_BASE_URL elsewhere to relocate it.
        base = os.environ.get("LOCAL2_BASE_URL", "http://localhost:8001/v1")
        os.environ.setdefault("LOCAL_API_KEY", "not-needed")
        return _openai_chat(model, system, messages, max_tokens, temperature,
                            base_url=base, api_key_env="LOCAL_API_KEY")
    if provider == "ollamathink":
        # Ollama's NATIVE /api/chat with think:true — the OpenAI-compat
        # endpoint drops reasoning-model CoT, but the native endpoint returns
        # it in a separate `thinking` field. Use this for reasoning agents
        # (DeepSeek-R1 etc.) where the chain-of-thought is the data.
        return _ollama_native_chat(model, system, messages, max_tokens, temperature, think=True)
    if provider == "ollamachat":
        # Same native endpoint but think:false — for NON-reasoning models we
        # still want on the native path (num_ctx control + identical commit
        # certifier) without the think:true that they reject. Used to hold the
        # code path constant across a reasoning-vs-not toggle experiment.
        return _ollama_native_chat(model, system, messages, max_tokens, temperature, think=False)
    if provider == "ollama":
        # Ollama's OpenAI-compatible endpoint on its own port, so an ollama
        # model (e.g. a fixed strong serpent) can run alongside the vLLM agent.
        # Model ids may contain colons (ollama:gemma4:latest) — partition on
        # the FIRST colon above keeps the tag intact.
        base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        os.environ.setdefault("OLLAMA_API_KEY", "not-needed")
        return _openai_chat(model, system, messages, max_tokens, temperature,
                            base_url=base, api_key_env="OLLAMA_API_KEY")
    raise ValueError(f"unknown provider in model spec: {model_spec!r}")
