# Architecture RFC: Trinity Remote (n8n on VPS)

## Goal
Decouple external integrations (VK, Social, Webhooks) from the local machine to maintain Zero-Clutter status (256GB SSD) while maintaining full control via Trinity Protocol.

## Architecture
- **Local (Reaper OS)**: Intelligence, Memory, Strategy (Conductor).
- **Remote (n8n on VPS)**: Integration Gateway, External API Bridge, Workflow Execution.

## Integration Path
1. **Bridge Protocol**:
    - Local Reaper sends JSON-payloads to n8n Webhook.
    - n8n performs API tasks (e.g., VK Post).
    - n8n sends Status-Webhook back to Reaper for log updates.

2. **Security**:
    - Webhook URL with Secret-key.
    - No direct shell access to local machine; unidirectional control.

3. **Management**:
    - Deploy n8n via Docker on VPS.
    - Proxy through Cloudflare Tunnel or simple Nginx reverse proxy.

## Pros
- **Lean Local OS**: No Node.js/Postgres bloat locally.
- **Always Online**: VK Bot runs 24/7 without local power-up requirements.
- **Trinity Synergy**: Reaper OS focuses on local cognitive tasks, n8n focuses on global connectivity.
