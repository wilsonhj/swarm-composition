import io
import json
import pathlib
import sys
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from adaption_backend import Adaption, ENDPOINT
from harness import Turns


class Response:
    status = 200
    def __init__(self, obj): self.body = json.dumps(obj).encode()
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self): return self.body


def good():
    return {"id": "r1", "model": "qwen3.5-397b", "status": "completed", "error": None,
            "incomplete_details": None, "usage": {"input_tokens": 100, "output_tokens": 20,
            "input_tokens_details": {"cached_tokens": 4}}, "output": [{"type": "message", "role": "assistant",
            "content": [{"type": "output_text", "text": "POST: "}, {"type": "output_text", "text": "hello"}]}]}


def backend(**kwargs):
    return Adaption("qwen3.5-397b", input_rate=.55, output_rate=3.5, max_credits=1,
                    key="secret-key", **kwargs)


class AdaptionTests(unittest.TestCase):
    def test_payload_usage_and_turn(self):
        b = backend()
        seen = []
        def send(req, timeout):
            seen.append(req)
            self.assertEqual(timeout, 180)
            return Response(good())
        with patch("urllib.request.urlopen", side_effect=send):
            raw, posted = Turns(b)("worker", "a", 0, "sys", "task")
        self.assertEqual((raw, posted), ("POST: hello", "hello"))
        req = seen[0]
        self.assertEqual(req.full_url, ENDPOINT)
        self.assertEqual(req.get_method(), "POST")
        self.assertEqual(req.get_header("Authorization"), "Bearer secret-key")
        self.assertEqual(json.loads(req.data), {"model": "qwen3.5-397b", "instructions": "sys", "input": "task",
            "max_output_tokens": 300, "temperature": 0, "tools": [], "tool_choice": "none",
            "agentic_memory": False, "store": False, "stream": False, "background": False})
        self.assertEqual(b.records[0]["raw"], good())
        self.assertEqual(b.tl.model, ["qwen3.5-397b"])
        self.assertAlmostEqual(b.estimated_credits, .000125)
        self.assertIsNone(b.cost)
        self.assertEqual(b.reserved_credits, 0)
        self.assertNotIn("secret-key", json.dumps(b.records))

    def test_invalid_responses_fail_and_account(self):
        variants = []
        for key, value in (("status", "incomplete"), ("error", {"message": "oops"}),
                           ("incomplete_details", {"reason": "max_output_tokens"}),
                           ("output", [{"type": "tool_call"}]), ("output", [])):
            d = good(); d[key] = value; variants.append(d)
        d = good(); d["output"][0]["content"].append({"type": "refusal", "refusal": "no"}); variants.append(d)
        d = good(); d["output"][0]["status"] = "incomplete"; variants.append(d)
        d = good(); d["output"][0]["content"][0]["refusal"] = "no"; variants.append(d)
        for response in variants:
            b = backend()
            with self.subTest(response=response), patch("urllib.request.urlopen", return_value=Response(response)):
                self.assertEqual(b("sys", "user"), "PASS")
                self.assertEqual(b.errors, 1)
                self.assertEqual(b.input_tokens, 100)
                self.assertEqual(b.reserved_credits, 0)
                self.assertTrue(b.stopped)

    def test_reasoning_is_preserved_but_not_returned(self):
        b = backend(); d = good()
        d["output"].insert(0, {"type": "reasoning", "status": None, "summary": [{"text": "private"}]})
        d["output"][1]["status"] = None
        with patch("urllib.request.urlopen", return_value=Response(d)):
            self.assertEqual(b("s", "u"), "POST: hello")
        self.assertEqual(b.records[0]["raw"], d)

    def test_missing_usage_and_model_mismatch_stop(self):
        for field in ("usage", "model"):
            b = backend(); d = good(); del d[field]
            with self.subTest(field=field), patch("urllib.request.urlopen", return_value=Response(d)) as send:
                self.assertEqual(b("s", "u"), "PASS")
                self.assertEqual(b("s", "u"), "PASS")
                self.assertEqual(send.call_count, 1)
                self.assertTrue(b.stopped)
                self.assertGreater(b.reserved_credits, 0) if field == "usage" else self.assertEqual(b.reserved_credits, 0)

    def test_http_timeout_and_bad_json_do_not_retry(self):
        class Bad(Response):
            def read(self): return b"not json"
        for effect in (HTTPError(ENDPOINT, 500, "secret-key", {}, io.BytesIO(b"secret-key")),
                       TimeoutError("secret-key"), URLError("secret-key"), Bad({})):
            b = backend()
            with self.subTest(effect=type(effect)), patch("urllib.request.urlopen", side_effect=effect if isinstance(effect, Exception) else None, return_value=effect) as send:
                self.assertEqual(b("s", "u"), "PASS")
                self.assertEqual(b("s", "u"), "PASS")
                self.assertEqual(send.call_count, 1)
                self.assertGreater(b.reserved_credits, 0)
                self.assertNotIn("secret-key", json.dumps(b.records))
                if isinstance(effect, HTTPError): self.assertEqual(b.records[0]["http_status"], 500)

    def test_retry_evidence_is_durable_and_does_not_retry(self):
        class BadJSON(Response):
            def read(self): return b'bad secret-key'

        cases = (
            (HTTPError(ENDPOINT, 504, "bad", {}, io.BytesIO(b"secret-key")), 504, None, False),
            (BadJSON({}), 200, None, False),
            (TimeoutError("secret-key"), None, "TimeoutError", True),
            (URLError("secret-key"), None, "URLError", True),
            (ConnectionError("secret-key"), None, "ConnectionError", True),
            (OSError("secret-key"), None, "OSError", False),
        )
        for effect, status, error_type, retryable in cases:
            events = []
            b = backend(record_sink=events.append)
            with self.subTest(effect=type(effect).__name__), patch(
                    "urllib.request.urlopen", side_effect=effect if isinstance(effect, Exception) else None,
                    return_value=effect) as send:
                self.assertEqual(b("s", "u"), "PASS")
                self.assertEqual(send.call_count, 1)
                self.assertTrue(b.stopped)
                self.assertGreater(b.reserved_credits, 0)
                record = events[-1]["record"]
                self.assertEqual(record["http_status"], status)
                self.assertEqual(record["transport_error_type"], error_type)
                self.assertEqual(record["retryable_transport"], retryable)
                self.assertNotIn("secret-key", json.dumps(events))
                if status == 504:
                    self.assertEqual(record["raw_body"], "[REDACTED]")

    def test_audit_events_and_redacted_bodies(self):
        for body, is_http in ((b'{"secret":"secret-key",', False),
                              (b'{"value": NaN, "key":"secret-key"}', False),
                              (b'{"value": 1e999}', False),
                              (b'upstream secret-key', True)):
            events = []
            b = backend(record_sink=events.append)
            class Raw(Response):
                def read(self): return body
            def send(req, timeout):
                self.assertEqual([e["event"] for e in events], ["attempt"])
                if is_http:
                    raise HTTPError(ENDPOINT, 500, "bad", {}, io.BytesIO(body))
                return Raw({})
            with self.subTest(body=body), patch("urllib.request.urlopen", side_effect=send):
                self.assertEqual(b("s", "u"), "PASS")
                self.assertEqual([e["event"] for e in events], ["attempt", "result"])
                self.assertEqual(events[0]["call_id"], events[1]["call_id"])
                self.assertIn("[REDACTED]", b.records[0]["raw_body"]) if b"secret-key" in body else self.assertEqual(b.records[0]["raw_body"], body.decode())
                self.assertNotIn("secret-key", json.dumps(events))

    def test_sink_failure_stops_before_send_and_preserves_record(self):
        def sink(event): raise OSError("disk full")
        b = backend(record_sink=sink)
        with patch("urllib.request.urlopen") as send, self.assertRaises(OSError):
            b("s", "u")
        send.assert_not_called()
        self.assertTrue(b.stopped)
        self.assertFalse(b.records[0]["sent"])
        self.assertEqual(b.records[0]["failure"], "record_sink_error")
        self.assertEqual(b.reserved_credits, 0)

    def test_budget_and_validation(self):
        b = Adaption("qwen3.5-397b", input_rate=1, output_rate=1, max_credits=.000001, key="k")
        with patch("urllib.request.urlopen") as send:
            self.assertEqual(b("s", "u"), "PASS")
            send.assert_not_called()
        self.assertEqual(b.calls, 0)
        with self.assertRaises(ValueError): backend(input_token_budget=True)
        for model in ("stack-abc", "harness", "x/y"):
            with self.assertRaises(ValueError): Adaption(model, input_rate=1, output_rate=1, max_credits=1, key="k")
        for n in (float("nan"), float("inf"), 0, -1, True):
            with self.assertRaises(ValueError): Adaption("model", input_rate=n, output_rate=1, max_credits=1, key="k")
        b = backend(input_token_budget=65)
        self.assertEqual(b("abc", "d"), "PASS")
        self.assertEqual(b.records[0]["failure"], "input_budget")


if __name__ == "__main__": unittest.main()
