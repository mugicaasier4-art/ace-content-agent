# Agent Self-Healing Notes

## Blockers encontrados (2026-04-05)

### 1. Typefully API — BLOQUEADA
- `api.typefully.com` NO está en la lista de hosts permitidos del proxy egress.
- Tanto `curl` como `WebFetch` fallan con 403 `host_not_allowed`.
- **Workaround**: Entregar los curls listos al usuario para que los ejecute manualmente o en Typefully app.
- **Fix permanente**: Añadir `api.typefully.com` a la allowlist del proxy.

### 2. Git push — BLOQUEADO
- `git push` falla con 403 "Permission denied to mugicaasier4-art".
- `mcp__github__push_files` falla con 403 "Resource not accessible by integration".
- `mcp__github__create_or_update_file` falla con 403 "Resource not accessible by integration".
- **Causa**: El GitHub MCP integration no tiene permisos de escritura (contents: write) al repo.
- **Workaround**: Commit local creado; el usuario debe pushear manualmente.
- **Fix permanente**: Dar permisos `contents: write` a la GitHub App/token para el repo `mugicaasier4-art/ace-content-agent`.

### 3. Gmail — Solo drafts, no envío
- No existe herramienta `gmail_send_draft` en el MCP de Gmail disponible.
- Solo se puede crear borrador (`gmail_create_draft`).
- **Workaround**: Crear draft y avisar al usuario para que pulse "Enviar" en Gmail.
- **Fix permanente**: Añadir scope `gmail.send` y herramienta `gmail_send_draft` al MCP.

## Qué SÍ funciona
- WebSearch para research
- Read/Write/Edit para archivos locales
- `git commit` local
- `mcp__Gmail__gmail_create_draft` para crear borradores
- GitHub MCP lectura (get_file_contents, list_commits, etc.)
