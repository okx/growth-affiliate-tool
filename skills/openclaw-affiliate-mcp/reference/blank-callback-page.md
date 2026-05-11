# The blank callback page is normal

This document exists because the single most common point of failure during install is users panicking when they see a blank page after clicking Authorize.

## What happens

When the user clicks **Authorize** on OKX, the browser is redirected to:

```
http://localhost:8787/callback?code=<code>&state=<state>
```

There is **no server running on the user's computer at port 8787**. The skill does not start one. As a result, the browser shows one of:

- A blank / white page
- "This site can't be reached"
- "localhost refused to connect"
- "ERR_CONNECTION_REFUSED"
- A blank tab title with no content

**All of these mean the same thing: the OAuth authorization succeeded.** The OKX server has issued an authorization `code` and put it in the redirect URL. We do not need a server to read it; we only need the user to copy the URL.

## What the user must do

1. **Do not close the tab.**
2. **Do not click reload.**
3. **Click into the address bar** (the URL bar at the top of the browser).
4. **Select the entire URL** (it starts with `http://localhost:8787/callback?...`).
5. **Copy and paste it back to the agent.**

## What the agent must say

Before sending the auth URL, the agent should warn the user about the blank page. After the user clicks Authorize, the agent should remind them again:

> The browser will show a **blank page** or "site can't be reached" \u2014 **this is correct**. Just copy the full URL from the address bar and paste it back to me.

Saying this twice is the difference between a 2-minute install and a 20-minute support conversation.

## Why we do it this way

Running a real local server to catch the redirect is possible, but it adds complexity:

- It requires an open port on the user's machine
- It does not work in headless / SSH / container environments
- It blocks the install if a firewall or another process is using port 8787
- It adds attack surface (a process listening for localhost callbacks)

Pasting the URL is universally portable, headless-friendly, and the security model is clean: the `code` is short-lived and PKCE-bound to a `code_verifier` only the agent has.

## Alternatives the user might propose

- **\"Can I just give you the code?\"** \u2014 Yes, the agent's `exchange.py` accepts a bare code. But pasting the full URL is preferred because the script also verifies `state`, which prevents accidentally using a code from a different session.\n- **\"My browser auto-closed the tab.\"** \u2014 The auth attempt cannot be resumed. Re-run `auth.py` and try again.\n- **\"Can I use a different redirect URI?\"** \u2014 No. The `redirect_uri` is bound to the DCR registration in `client.json`. Changing it requires re-registering.\n"