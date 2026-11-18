---
id: cloudflare-via-mcp
trigger: when checking or changing Cloudflare configuration (DNS, Turnstile, Workers, secrets)
confidence: 0.8
domain: workflow
source: approved
scope: global
---

# Cloudflare cez MCP server

## Action
Nastavenia v Cloudflare zisťuj a meň cez Cloudflare MCP server; ručné `dig`/`curl` použi len na overenie výsledku a pri rozpore over priamo v dashboarde, lebo zle zapísaný dotaz vráti prázdny výsledok a vyzerá ako chýbajúci záznam.
