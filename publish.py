"""
Publica un post de LinkedIn y un hilo de X vía Typefully API.

Uso:
    python publish.py --linkedin-post "texto" --x-thread "t1|||t2|||t3" --delay-hours 4

Variables de entorno requeridas:
    TYPEFULLY_API_KEY           — API key de Typefully
    TYPEFULLY_LI_SOCIAL_SET_ID  — social_set_id para LinkedIn (fallback: 295131)
    TYPEFULLY_X_SOCIAL_SET_ID   — social_set_id para X
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone

import httpx

BASE_URL = "https://api.typefully.com/v2"


def _headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def create_draft(api_key: str, social_set_id: str, platform: str, posts: list[str]) -> str:
    """
    Crea un draft en Typefully para la plataforma indicada.
    platform: "linkedin" o "x"
    posts: lista de textos (1 elemento para LinkedIn, N para thread de X)
    Devuelve el draft_id como string.
    """
    url = f"{BASE_URL}/social-sets/{social_set_id}/drafts"
    body = {
        "platforms": {
            platform: {
                "enabled": True,
                "posts": [{"text": t} for t in posts],
            }
        }
    }
    try:
        response = httpx.post(url, headers=_headers(api_key), json=body, timeout=30)
    except httpx.RequestError as exc:
        print(f"[ERROR] create_draft({platform}) — network error: {exc}", file=sys.stderr)
        sys.exit(1)
    if not response.is_success:
        print(
            f"[ERROR] create_draft({platform}) — HTTP {response.status_code}: {response.text}",
            file=sys.stderr,
        )
        sys.exit(1)
    data = response.json()
    if "id" not in data:
        print(
            f"[ERROR] create_draft({platform}) — respuesta sin clave 'id': {data}",
            file=sys.stderr,
        )
        sys.exit(1)
    return str(data["id"])


def schedule_draft(
    api_key: str, social_set_id: str, draft_id: str, publish_at: datetime
) -> dict:
    """
    Programa un draft existente para publish_at (datetime UTC).
    Devuelve el body de respuesta de la API.
    """
    url = f"{BASE_URL}/social-sets/{social_set_id}/drafts/{draft_id}"
    body = {"publish_at": publish_at.strftime("%Y-%m-%dT%H:%M:%SZ")}
    try:
        response = httpx.patch(url, headers=_headers(api_key), json=body, timeout=30)
    except httpx.RequestError as exc:
        print(f"[ERROR] schedule_draft({draft_id}) — network error: {exc}", file=sys.stderr)
        sys.exit(1)
    if not response.is_success:
        print(
            f"[ERROR] schedule_draft({draft_id}) — HTTP {response.status_code}: {response.text}",
            file=sys.stderr,
        )
        sys.exit(1)
    return response.json()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Publica un post de LinkedIn y un hilo de X vía Typefully."
    )
    parser.add_argument("--linkedin-post", required=True, help="Texto del post de LinkedIn")
    parser.add_argument(
        "--x-thread",
        required=True,
        help='Tweets separados por "|||" (ej: "tweet1|||tweet2|||tweet3")',
    )
    parser.add_argument(
        "--delay-hours",
        type=float,
        default=4.0,
        help="Horas de delay desde ahora para programar el post (default: 4.0)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    api_key = os.environ.get("TYPEFULLY_API_KEY")
    if not api_key:
        print("[ERROR] TYPEFULLY_API_KEY no está definida en el entorno.", file=sys.stderr)
        sys.exit(1)

    li_social_set_id = os.environ.get("TYPEFULLY_LI_SOCIAL_SET_ID", "295131")
    x_social_set_id = os.environ.get("TYPEFULLY_X_SOCIAL_SET_ID")
    if not x_social_set_id:
        print("[ERROR] TYPEFULLY_X_SOCIAL_SET_ID no está definida en el entorno.", file=sys.stderr)
        sys.exit(1)

    publish_at = datetime.now(tz=timezone.utc) + timedelta(hours=args.delay_hours)
    publish_at_str = publish_at.strftime("%Y-%m-%dT%H:%M:%SZ")

    # --- LinkedIn ---
    li_draft_id = create_draft(api_key, li_social_set_id, "linkedin", [args.linkedin_post])
    schedule_draft(api_key, li_social_set_id, li_draft_id, publish_at)
    print(f"[LinkedIn] Draft ID: {li_draft_id} | Programado para: {publish_at_str}")

    # --- X (thread) ---
    tweets = [t.strip() for t in args.x_thread.split("|||") if t.strip()]
    if not tweets:
        print("[ERROR] --x-thread no contiene tweets válidos tras el split por '|||'.", file=sys.stderr)
        sys.exit(1)
    x_draft_id = create_draft(api_key, x_social_set_id, "x", tweets)
    schedule_draft(api_key, x_social_set_id, x_draft_id, publish_at)
    print(f"[X] Draft ID: {x_draft_id} | Programado para: {publish_at_str}")


if __name__ == "__main__":
    main()
