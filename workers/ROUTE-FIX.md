# Worker Route Issue - 521 Error

## Problem
Getting HTTP 521 error - means worker isn't executing or route pattern doesn't match

## Solution: Fix Route Pattern

Go to Cloudflare Dashboard and update the route:

### Current Route (Not Working)
- Pattern: `telegrams.app/chat_dota2`
- Error: 521

### Try These Patterns (in order):

**Option 1: Add Wildcard**
- Pattern: `telegrams.app/chat_dota2*`
- Zone: telegrams.app
- Worker: telegram-proxy-payload

**Option 2: Full URL with Protocol**
- Pattern: `https/telegrams.app/chat_dota2*`

**Option 3: Subdomain Wildcard**
- Pattern: `*telegrams.app/chat_dota2*`

### Steps:
1. Go to Workers & Pages
2. Click telegram-proxy-payload
3. Settings → Triggers → Routes
4. Edit or delete existing route
5. Add new route with wildcard pattern
6. Save and test

### Test After Update:
```bash
curl -I "https/telegrams.app/chat_dota2?test=$(date +%s)"
```

Should return HTTP 200, not 521

