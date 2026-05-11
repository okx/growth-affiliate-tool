# OKX Affiliate MCP — OAuth endpoints

All endpoints live under `https://www.okx.com`. Discovery exists but not all endpoints follow the discovery defaults; the values below are what actually work.

## Discovery (FYI only)

```
GET https://www.okx.com/.well-known/oauth-authorization-server
```

Returns the standard metadata. Useful to inspect; not required at runtime since this skill hardcodes the endpoints we verified.

## Dynamic Client Registration (DCR)

```
POST https://www.okx.com/api/v5/mcp/auth/register
Content-Type: application/json

{
  "client_name": "OpenClaw Affiliate MCP Client",
  "redirect_uris": ["http://localhost:8787/callback"],
  "scope": "live:read"
}
```

Response includes `client_id` (no `client_secret` — this is a public client using PKCE).

## Authorize (browser)

```
https://www.okx.com/account/oauth?
  response_type=code
  &client_id=...
  &redirect_uri=http://localhost:8787/callback
  &scope=live:read
  &code_challenge=...
  &code_challenge_method=S256
  &state=...
  &flow=code
  &resource=https://www.okx.com/api/v1/mcp/growth-affiliate-mcp
```

Required quirks:
- `flow=code` — without it OKX may show a non-OAuth UI
- `resource=...` — without it the eventual token exchange fails

After approval the user is redirected to:

```
http://localhost:8787/callback?code=<code>&state=<state>
```

The redirect target does **not** need a real listener. The agent reads `code` and `state` from the URL the user pastes back.

## Token (exchange + refresh)

```
POST https://www.okx.com/api/v5/mcp/auth/token
Content-Type: application/x-www-form-urlencoded
```

### Authorization code

```
grant_type=authorization_code
client_id=<client_id>
redirect_uri=http://localhost:8787/callback
code=<code>
code_verifier=<pkce verifier>
resource=https://www.okx.com/api/v1/mcp/growth-affiliate-mcp
```

### Refresh

```
grant_type=refresh_token
client_id=<client_id>
refresh_token=<refresh_token>
resource=https://www.okx.com/api/v1/mcp/growth-affiliate-mcp
```

Both responses (200 OK):

```json
{
  "access_token": "eyJhbGciOi...",
  "expires_in": 3600,
  "refresh_token": "...",
  "scope": "live:asset_transfer live:earn live:trade live:read",
  "token_type": "Bearer"
}
```

## MCP endpoint (the actual API)

```
https://www.okx.com/api/v1/mcp/growth-affiliate-mcp
```

Call with `Authorization: Bearer <access_token>`. This is also the `resource` value used everywhere in the OAuth flow, and matches the `aud` claim of issued access tokens.
