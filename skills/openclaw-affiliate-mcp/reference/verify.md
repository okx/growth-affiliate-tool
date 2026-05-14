# Verifying the access token

Once `token.json` exists, sanity-check the credentials before reporting success.

## Decode the JWT (offline, no network)

The access token is a JWT. Base64-decode the middle segment to inspect:

```bash
python3 -c '
import base64, json, sys
tok = json.load(open("'"$HOME"'/.openclaw/data/okx-affiliate-mcp/token.json"))["access_token"]
mid = tok.split(".")[1] + "=="
print(json.dumps(json.loads(base64.urlsafe_b64decode(mid)), indent=2))
'
```

Useful claims:
- `aud` — should be `https://www.okx.com/api/v1/mcp/growth-affiliate-mcp`
- `scp` — granted scopes
- `exp` — expiry (Unix sec)
- `uid` — opaque user id

If `aud` is not the affiliate MCP, the `resource` parameter was wrong somewhere.

## Live MCP call

The cheapest way to confirm the token actually works is to call the MCP endpoint with `Authorization: Bearer <access_token>`. Exact tool names depend on the MCP's published schema; consult the OKX Affiliate MCP documentation for the current tool list.

> ⚠️ The MCP endpoint sits behind Cloudflare WAF. Always send a browser User-Agent on the call, or it returns `403 Cloudflare Error 1010` even though the token is valid. See `reference/known-issues.md`.

Minimal Python check:

```python
import json, urllib.request
from pathlib import Path

tok = json.loads(Path("~/.openclaw/data/okx-affiliate-mcp/token.json").expanduser().read_text())["access_token"]

req = urllib.request.Request(
    "https://www.okx.com/api/v1/mcp/growth-affiliate-mcp",
    headers={
        "Authorization": f"Bearer {tok}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
    },
    data=b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}',
)
with urllib.request.urlopen(req, timeout=15) as r:
    print(r.status, r.read()[:300])
```

Return code 200 with a JSON body = healthy. Return code 401 = token rejected (try `refresh.py`, then re-auth). Return code 403 with Cloudflare 1010 = User-Agent header is missing or non-browser.
