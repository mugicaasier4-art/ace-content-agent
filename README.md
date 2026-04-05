# AI Content Agent — LinkedIn + X

Sistema automatizado que cada 2 días investiga tendencias de AI/automation, elige el tema con más potencial de ROI para la audiencia de Asier Mugica, genera un post LinkedIn en español + hilo X adaptado, y los sube como drafts a Typefully (+4h de ventana de revisión). Notifica por Telegram.

## Archivos

| Archivo | Propósito |
|---|---|
| `agent-prompt.md` | El prompt que ejecuta el agente scheduled. No editar salvo que quieras cambiar el comportamiento. |
| `real-results.md` | Métricas reales de clientes. **Asier lo alimenta manualmente.** Crítico para que los posts tengan ejemplos reales. |
| `published-topics-log.json` | Historial de temas publicados. El agente lo actualiza automáticamente para evitar repeticiones. |
| `publish.py` | Script que crea drafts en Typefully (LinkedIn + X). Lo ejecuta el agente. |

## Cómo actualizar real-results.md

Cada vez que consigas un resultado concreto de un cliente (métrica, before/after, testimonio), añádelo siguiendo la plantilla al final del archivo. Cuantos más datos reales tengas, mejores serán los posts generados.

Ejemplos de cosas que vale la pena registrar:
- "El cliente pasó de X% a Y% de conversión"
- "Ahorramos Z horas semanales de trabajo manual"
- "Respondemos en X minutos en lugar de Y horas"

## Cómo funciona el schedule

El agente corre automáticamente cada 2 días a las 9 AM (hora España). No requiere intervención manual. Si quieres cancelar un post antes de que se publique:
1. Abre Typefully
2. Busca el draft (tendrás 4 horas desde la notificación de Telegram)
3. Elimínalo o edítalo

## Variables de entorno requeridas

En el `.env` raíz del proyecto:
- `TYPEFULLY_API_KEY` — ya existe
- `TYPEFULLY_X_SOCIAL_SET_ID` — ya existe
- `TYPEFULLY_LI_SOCIAL_SET_ID` — añadir con el social_set_id de LinkedIn (actualmente hardcoded como 295131)
- `ANTHROPIC_API_KEY` — ya existe

## Logs

Cada ejecución del agente genera un log en `active/content-agent-log-YYYY-MM-DD.md` con:
- Los posts encontrados en el research
- El tema elegido y su puntuación
- El post LinkedIn generado
- El hilo X generado
- El resultado de la publicación en Typefully
