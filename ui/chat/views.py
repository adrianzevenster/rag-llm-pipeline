import json
from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from .services import RagBackendClient

client = RagBackendClient()

def chat_page(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "chat/chat.html",
        {
            "default_agent": settings.DEFAULT_AGENT_NAME,
            "backend_base_url": settings.BACKEND_BASE_URL,
        },
    )

@require_http_methods(["POST"])
def chat_api(request: HttpRequest) -> JsonResponse:
    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    agent_name = (body.get("agent_name") or settings.DEFAULT_AGENT_NAME).strip()
    message = (body.get("message") or "").strip()

    if not message:
        return JsonResponse({"ok": False, "error": "Message cannot be empty"}, status=400)

    result = client.chat(agent_name=agent_name, message=message)
    if not result.ok:
        return JsonResponse(
            {"ok": False, "error": result.error or "Backend request failed", "status_code": result.status_code},
            status=502,
        )

    data = result.data or {}

    # UI expects these fields; backend can return more (tool_calls, retrieved, etc.)
    output = data.get("output", "")
    run_id = data.get("run_id", "")
    agent = data.get("agent_name", agent_name)

    # If output is structured, stringify for display
    if not isinstance(output, str):
        output = json.dumps(output, ensure_ascii=False, indent=2)

    return JsonResponse(
        {
            "ok": True,
            "agent_name": agent,
            "run_id": str(run_id) if run_id is not None else "",
            "output": output,
            "raw": data,
        }
    )

def health_page(request: HttpRequest) -> HttpResponse:
    result = client.health()
    return render(request, "chat/health.html", {"result": result})
