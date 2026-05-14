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

Return code 200 with a JSON body = healthy. Return code 401 = token rejected (try `refresh.py`, then re-auth).
