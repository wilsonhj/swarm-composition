"""Isolated Adaption Responses backend. Credit estimates are not spending guarantees.

The UTF-8 byte guard plus 64 bytes of framing is a conservative heuristic, not a
mathematical tokenizer bound. Unreported charges and reasoning may exceed estimates.
"""
import json
import math
import os
import re
import time
import urllib.error
import urllib.request
import uuid

from harness import Backend

ENDPOINT = "https://api.prod.adaptionlabs.ai/api/v1/responses"


def _positive_number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return value


def _positive_int(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


class Adaption(Backend):
    def __init__(self, model, *, input_rate, output_rate, max_credits, max_output_tokens=300,
                 input_token_budget=2500, key=None, record_sink=None):
        if (not isinstance(model, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", model)
                or re.search(r"(?:stack|harness)", model, re.I)):
            raise ValueError("model must be a hosted model ID, not a stack or harness")
        self.model = model
        self.input_rate = _positive_number(input_rate, "input_rate")
        self.output_rate = _positive_number(output_rate, "output_rate")
        self.max_credits = _positive_number(max_credits, "max_credits")
        self.max_output_tokens = _positive_int(max_output_tokens, "max_output_tokens")
        self.input_token_budget = _positive_int(input_token_budget, "input_token_budget")
        self.key = os.environ.get("ADAPTION_API_KEY", "") if key is None else key
        if not isinstance(self.key, str) or not self.key.strip():
            raise ValueError("ADAPTION_API_KEY is required")
        self._init_counters(cost=None)
        if record_sink is not None and not callable(record_sink):
            raise ValueError("record_sink must be callable")
        self.record_sink = record_sink
        self.records = []
        self.estimated_credits = 0.0
        self.reserved_credits = 0.0
        self.input_tokens = self.output_tokens = 0
        self.stopped = False
        self.reservation = (input_token_budget * input_rate + max_output_tokens * output_rate) / 1_000_000
        if not math.isfinite(self.reservation):
            raise ValueError("reservation must be finite")

    def totals(self):
        with self.lock:
            return {"calls": self.calls, "errors": self.errors, "fail_reasons": dict(self.fail_reasons),
                    "estimated_credits": self.estimated_credits, "reserved_credits": self.reserved_credits,
                    "input_tokens": self.input_tokens, "output_tokens": self.output_tokens,
                    "models": sorted(self.models), "cost": None, "stopped": self.stopped}

    def _redact(self, obj):
        if isinstance(obj, str):
            return obj.replace(self.key, "[REDACTED]")
        if isinstance(obj, list):
            return [self._redact(x) for x in obj]
        if isinstance(obj, dict):
            return {self._redact(k): ("[REDACTED]" if k == "error" and v is not None else self._redact(v))
                    for k, v in obj.items()}
        if isinstance(obj, float) and not math.isfinite(obj):
            return "[NONFINITE]"
        if obj is None or isinstance(obj, (bool, int, float)):
            return obj
        return self._redact(repr(obj))

    def __call__(self, system, user):
        self.tl.model = None
        request = {"model": self.model, "instructions": system, "input": user,
                   "max_output_tokens": self.max_output_tokens, "temperature": 0,
                   "tools": [], "tool_choice": "none", "agentic_memory": False,
                   "store": False, "stream": False, "background": False}
        record = {"call_id": str(uuid.uuid4()), "raw_body": None, "request": self._redact(request), "sent": False, "raw": None, "http_status": None,
                  "model": None, "status": None, "error": None, "incomplete_details": None,
                  "usage": None, "failure": None, "elapsed_ms": None}
        def emit(event):
            if self.record_sink is not None:
                try:
                    self.record_sink(json.loads(json.dumps(self._redact(event), allow_nan=False)))
                except BaseException:
                    with self.lock: self.stopped = True
                    raise
        def finalize():
            with self.lock: self.records.append(record)
            emit({"event": "result", "call_id": record["call_id"], "record": record})
        def fail(reason, stop=True):
            record["failure"] = reason
            with self.lock:
                if stop: self.stopped = True
            result = self._fail(reason)
            finalize()
            return result
        if not isinstance(system, str) or not isinstance(user, str):
            return fail("invalid_input")
        try:
            input_size = len(system.encode("utf-8")) + len(user.encode("utf-8")) + 64
        except UnicodeError:
            return fail("invalid_input")
        if input_size > self.input_token_budget:
            return fail("input_budget")
        with self.lock:
            if self.stopped:
                reason = "backend_stopped"
            elif self.estimated_credits + self.reserved_credits + self.reservation > self.max_credits:
                reason = "credit_budget"
            else:
                reason = None
                self.reserved_credits += self.reservation
        if reason:
            return fail(reason)
        try:
            emit({"event": "attempt", "call_id": record["call_id"], "request": record["request"]})
        except BaseException:
            with self.lock:
                self.reserved_credits -= self.reservation
                record["failure"] = "record_sink_error"
                self.records.append(record)
            self._fail("record_sink_error")
            raise
        with self.lock:
            self.calls += 1
            record["sent"] = True
        payload = json.dumps(request, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(ENDPOINT, data=payload, method="POST", headers={
            "Authorization": "Bearer " + self.key, "Content-Type": "application/json"})
        start = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=180) as response:
                record["http_status"] = response.status
                body = response.read()
                if not isinstance(response.status, int) or isinstance(response.status, bool) or not 200 <= response.status < 300:
                    record["raw_body"] = self._redact(body.decode("utf-8", errors="replace"))
                    data = None
                else:
                    data = "pending"
                try:
                    def finite_float(value):
                        number = float(value)
                        if not math.isfinite(number): raise ValueError("nonfinite JSON number")
                        return number
                    if data == "pending":
                        data = json.loads(body, parse_float=finite_float, parse_constant=lambda value: (_ for _ in ()).throw(ValueError("invalid JSON constant")))
                except (ValueError, UnicodeError):
                    record["raw_body"] = self._redact(body.decode("utf-8", errors="replace"))
                    raise
        except urllib.error.HTTPError as exc:
            record["http_status"] = exc.code
            try:
                record["raw_body"] = self._redact(exc.read().decode("utf-8", errors="replace"))
            except Exception:
                record["raw_body"] = None
            record["elapsed_ms"] = round((time.monotonic() - start) * 1000)
            return fail("http_error", stop=True)
        except (OSError, ValueError, UnicodeError):
            record["elapsed_ms"] = round((time.monotonic() - start) * 1000)
            return fail("transport_or_json_error", stop=True)
        record["elapsed_ms"] = round((time.monotonic() - start) * 1000)
        if not isinstance(record["http_status"], int) or isinstance(record["http_status"], bool) or not 200 <= record["http_status"] < 300:
            return fail("http_error")
        record["raw"] = self._redact(data)
        # Provider error text may echo credentials or other sensitive input.
        if isinstance(record["raw"], dict) and record["raw"].get("error") is not None:
            record["raw"]["error"] = "[REDACTED]"
        if not isinstance(data, dict):
            return fail("invalid_response", stop=True)
        served = data.get("model")
        if isinstance(served, str) and served:
            self.tl.model = [served]
            with self.lock: self.models.add(served)
        record.update(model=self._redact(served), status=self._redact(data.get("status")),
                      error="[REDACTED]" if data.get("error") is not None else None,
                      incomplete_details=self._redact(data.get("incomplete_details")),
                      usage=self._redact(data.get("usage")))
        usage = data.get("usage")
        if (not isinstance(usage, dict) or any(isinstance(usage.get(k), bool) or
                not isinstance(usage.get(k), int) or usage[k] < 0 for k in ("input_tokens", "output_tokens"))):
            return fail("missing_or_invalid_usage", stop=True)
        inp, out = usage["input_tokens"], usage["output_tokens"]
        try:
            credits = (inp * self.input_rate + out * self.output_rate) / 1_000_000
        except OverflowError:
            return fail("invalid_usage_cost", stop=True)
        if not math.isfinite(credits):
            return fail("invalid_usage_cost", stop=True)
        with self.lock:
            self.input_tokens += inp
            self.output_tokens += out
            self.estimated_credits += credits
            self.reserved_credits -= self.reservation
            exceeded = self.estimated_credits + self.reserved_credits > self.max_credits
            if exceeded: self.stopped = True
        record["estimated_credits"] = credits
        if not isinstance(served, str) or served != self.model:
            return fail("model_mismatch", stop=True)
        if exceeded: return fail("credit_budget_exceeded", stop=True)
        if data.get("status") != "completed": return fail("status_not_completed")
        if data.get("error") is not None: return fail("response_error")
        if data.get("incomplete_details") is not None: return fail("incomplete")
        output = data.get("output")
        if not isinstance(output, list) or not output: return fail("invalid_output")
        parts = []
        for item in output:
            # Hosted responses serialize absent item status as null, including reasoning.
            # The top-level response must still be completed; partial item states fail.
            if not isinstance(item, dict) or item.get("error") is not None or item.get("status") not in (None, "completed"):
                return fail("unexpected_output")
            if item.get("type") == "reasoning":
                continue
            if item.get("type") != "message" or item.get("role") != "assistant":
                return fail("unexpected_output")
            content = item.get("content")
            if not isinstance(content, list) or not content: return fail("invalid_output")
            for part in content:
                if (not isinstance(part, dict) or part.get("type") != "output_text"
                        or part.get("refusal") is not None or part.get("error") is not None
                        or not isinstance(part.get("text"), str)):
                    return fail("unexpected_content")
                parts.append(part["text"])
        text = "".join(parts).strip()
        if not text: return fail("empty_output")
        finalize()
        return text
