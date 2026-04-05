"""
GitHub Action script: lee drafts/pending.json y publica en Typefully.

Secrets requeridos en el repo:
  TYPEFULLY_API_KEY       — API key de Typefully
  TYPEFULLY_SOCIAL_SET_ID — ID del social set (cubre LinkedIn y X)
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

API_KEY = os.environ["TYPEFULLY_API_KEY"]
SOCIAL_SET_ID = os.environ["TYPEFULLY_SOCIAL_SET_ID"]
BASE_URL = "https://api.typefully.com/v2"
DRAFT_FILE = Path("drafts/pending.json")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


def create_draft(platform: str, posts: list[str]) -> str:
    url = f"{BASE_URL}/social-sets/{SOCIAL_SET_ID}/drafts"
    body = {
        "platforms": {
            platform: {
                "enabled": True,
                "posts": [{"text": t} for t in posts],
            }
        }
    }
    r = httpx.post(url, headers=HEADERS, json=body, timeout=30)
    if not r.is_success:
        print(f"[ERROR] create_draft({platform}) HTTP {r.status_code}: {r.text}", file=sys.stderr)
        sys.exit(1)
    data = r.json()
    if "id" not in data:
        print(f"[ERROR] create_draft({platform}) sin 'id': {data}", file=sys.stderr)
        sys.exit(1)
    return str(data["id"])


def schedule_draft(draft_id: str, publish_at: str) -> None:
    url = f"{BASE_URL}/social-sets/{SOCIAL_SET_ID}/drafts/{draft_id}"
    r = httpx.patch(url, headers=HEADERS, json={"publish_at": publish_at}, timeout=30)
    if not r.is_success:
        print(f"[ERROR] schedule_draft({draft_id}) HTTP {r.status_code}: {r.text}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    if not DRAFT_FILE.exists():
        print(f"[ERROR] No existe {DRAFT_FILE}", file=sys.stderr)
        sys.exit(1)

    draft = json.loads(DRAFT_FILE.read_text())

    linkedin_text = draft.get("linkedin")
    x_thread = draft.get("x_thread", [])
    publish_at = draft.get("publish_at")

    if not linkedin_text:
        print("[ERROR] Campo 'linkedin' vacío o ausente en pending.json", file=sys.stderr)
        sys.exit(1)
    if not x_thread:
        print("[ERROR] Campo 'x_thread' vacío o ausente en pending.json", file=sys.stderr)
        sys.exit(1)
    if not publish_at:
        # Default: +4h desde ahora
        publish_at = (datetime.now(tz=timezone.utc) + timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M:%SZ")
        print(f"[WARN] publish_at no especificado, usando +4h: {publish_at}")

    # LinkedIn
    li_id = create_draft("linkedin", [linkedin_text])
    schedule_draft(li_id, publish_at)
    print(f"[LinkedIn] Draft ID: {li_id} | Programado: {publish_at}")

    # X thread
    x_id = create_draft("x", x_thread)
    schedule_draft(x_id, publish_at)
    print(f"[X] Draft ID: {x_id} | Programado: {publish_at}")

    print("\n✓ Publicación programada en Typefully.")


if __name__ == "__main__":
    main()
