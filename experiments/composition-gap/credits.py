"""Print OpenRouter key usage/limit/remaining (GET /api/v1/key). Never prints the key."""
import json, urllib.error, urllib.request
from harness import openrouter_key

if __name__ == "__main__":
    req = urllib.request.Request("https://openrouter.ai/api/v1/key", headers={"Authorization": f"Bearer {openrouter_key()}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r: d = json.loads(r.read())["data"]
    except urllib.error.HTTPError as e:
        raise SystemExit(f"OpenRouter HTTP {e.code} from /api/v1/key")
    lim, rem = d.get("limit"), d.get("limit_remaining")
    print(f"label={d.get('label')}")
    print(f"usage=${d.get('usage', 0):.4f}  limit={'unlimited' if lim is None else f'${lim:.2f}'}  "
          f"remaining={'n/a (no key limit)' if rem is None else f'${rem:.2f}'}")
