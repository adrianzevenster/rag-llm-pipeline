from dataclasses import dataclass
from typing import Any, Dict, Optional
import httpx
from django.conf import settings

@dataclass
class BackendResult:
    ok: bool
    status_code: int
    data: Optional[Dict[str, Any]] = None
    error: str = ""

class RagBackendClient:
    def __init__(self) -> None:
        self.base_url = settings.BACKEND_BASE_URL
        self.timeout = httpx.Timeout(
            connect=10.0,
            read=settings.BACKEND_TIMEOUT_SECONDS,
            write=10.0,
            pool=10.0,
        )

    def chat(self, agent_name: str, message: str) -> BackendResult:
        url = f"{self.base_url}/chat"
        payload = {"agent_name": agent_name, "message": message}
        try:
            r = httpx.post(url, json=payload, timeout=self.timeout)
            data = _safe_json(r)
            return BackendResult(ok=r.is_success, status_code=r.status_code, data=data)
        except Exception as e:
            return BackendResult(ok=False, status_code=0, error=str(e))

    def health(self) -> BackendResult:
        url = f"{self.base_url}/health"
        try:
            r = httpx.get(url, timeout=self.timeout)
            data = _safe_json(r)
            return BackendResult(ok=r.is_success, status_code=r.status_code, data=data)
        except Exception as e:
            return BackendResult(ok=False, status_code=0, error=str(e))

def _safe_json(resp: httpx.Response) -> Dict[str, Any]:
    try:
        return resp.json()
    except Exception:
        return {"raw_text": resp.text}
