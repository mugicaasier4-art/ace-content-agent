# Agent Self-Healing Notes

> Actualizado: 2026-04-05
> Lee este archivo al inicio de cada ejecución para evitar errores conocidos.

---

## ARQUITECTURA ACTUAL (cómo publicar)

### Flujo correcto — 3 pasos

1. **Escribir** `drafts/pending.json` con el contenido generado (usa `schema.json` como referencia)
2. **Pushear** via GitHub API con PAT (ver sección de git abajo)
3. **GitHub Action** se activa automáticamente y publica en Typefully

El agente NO llama directamente a Typefully API. El proxy del entorno bloquea `api.typefully.com`.

### Cómo escribir pending.json

```json
{
  "date": "2026-04-05",
  "topic": "tema en 1 línea",
  "pillar": "caso",
  "publish_at": "2026-04-05T12:00:00Z",
  "linkedin": "texto completo\ncon saltos de línea\ncomo este",
  "x_thread": [
    "tweet 1 (<280 chars)",
    "tweet 2 (<280 chars)",
    "tweet 3 (<280 chars)"
  ]
}
```

### Cómo pushear archivos (GitHub API con PAT)

El `git push` normal está bloqueado por el proxy. Usar GitHub REST API:

```python
import base64, json
import subprocess

PAT = os.environ.get("GITHUB_PAT")  # Configurado en ~/.bashrc o variable de entorno

def push_file(path, content_str, commit_msg, sha=None):
    """
    path: ruta en el repo, ej: "drafts/pending.json"
    content_str: contenido como string
    sha: SHA actual del archivo en el repo (None si es nuevo)
    """
    b64 = base64.b64encode(content_str.encode()).decode()
    body = {"message": commit_msg, "content": b64}
    if sha:
        body["sha"] = sha
    import urllib.request
    req = urllib.request.Request(
        f"https://api.github.com/repos/mugicaasier4-art/ace-content-agent/contents/{path}",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {PAT}", "Content-Type": "application/json"},
        method="PUT"
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

# Para obtener SHA actual de un archivo:
def get_sha(path):
    import urllib.request
    req = urllib.request.Request(
        f"https://api.github.com/repos/mugicaasier4-art/ace-content-agent/contents/{path}",
        headers={"Authorization": f"Bearer {PAT}"}
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read()).get("sha")
    except:
        return None  # archivo nuevo
```

O usar curl directamente:
```bash
PAT="$GITHUB_PAT"
CONTENT=$(base64 -w0 drafts/pending.json)
SHA=$(curl -s -H "Authorization: Bearer $PAT" \
  "https://api.github.com/repos/mugicaasier4-art/ace-content-agent/contents/drafts/pending.json" \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('sha',''))" 2>/dev/null)

curl -s -X PUT \
  -H "Authorization: Bearer $PAT" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/mugicaasier4-art/ace-content-agent/contents/drafts/pending.json" \
  -d "{\"message\":\"content: draft $(date +%F)\",\"content\":\"$CONTENT\",\"sha\":\"$SHA\"}"
```

---

## NOTIFICACIÓN EMAIL

Gmail MCP funciona para crear borradores:
```
mcp__Gmail__gmail_create_draft(
  to="asiermugica.ia@gmail.com",
  subject="[Content Agent] Post listo — TEMA",
  body="POST LINKEDIN:\n...\n\nHILO X:\n..."
)
```
El usuario envía el borrador manualmente (1 clic en Gmail).
No existe herramienta `gmail_send_draft` en este entorno.

---

## ACTUALIZAR published-topics-log.json

1. Leer SHA actual del archivo en el repo
2. Modificar el contenido localmente
3. Pushear con GitHub API usando el SHA obtenido

Ejemplo:
```bash
PAT="$GITHUB_PAT"
# Obtener SHA
SHA=$(curl -s -H "Authorization: Bearer $PAT" \
  "https://api.github.com/repos/mugicaasier4-art/ace-content-agent/contents/published-topics-log.json" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['sha'])")
# Push con nuevo contenido
CONTENT=$(base64 -w0 published-topics-log.json)
curl -s -X PUT \
  -H "Authorization: Bearer $PAT" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/mugicaasier4-art/ace-content-agent/contents/published-topics-log.json" \
  -d "{\"message\":\"chore: log topic $(date +%F)\",\"content\":\"$CONTENT\",\"sha\":\"$SHA\"}"
```

---

## HOSTS BLOQUEADOS POR EL PROXY

El entorno bloquea todo excepto la allowlist. NO intentar:
- `api.typefully.com` — BLOQUEADO (usar GitHub Action)
- `api.github.com` vía git — BLOQUEADO (usar curl con PAT)

Hosts que SÍ funcionan via curl/WebSearch/WebFetch:
- `github.com` (API REST)
- `api.github.com`
- Cualquier host de la allowlist del proxy

---

## SECRETS DEL REPO (GitHub Actions)

Estos secrets deben estar configurados en el repo para que el Action funcione:
- `TYPEFULLY_API_KEY` = `Az2jEmpgzWxax3vjCH4UftZfuFSLe979`
- `TYPEFULLY_SOCIAL_SET_ID` = `295131`

Configurarlos en: github.com/mugicaasier4-art/ace-content-agent/settings/secrets/actions
