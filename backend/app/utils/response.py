from typing import Any, Dict, List, Optional
from flask import jsonify, Response

def api_response(
    success: bool = True,
    message: str = "",
    data: Optional[Any] = None,
    errors: Optional[List[Dict[str, Any]]] = None,
    meta: Optional[Dict[str, Any]] = None,
    status_code: int = 200,
) -> tuple[Response, int]:
    """Generate a consistent, structured JSON API response."""
    payload: Dict[str, Any] = {
        "success": success,
        "message": message,
    }

    if data is not None:
        payload["data"] = data

    if errors:
        payload["errors"] = errors

    if meta is not None:
        payload["meta"] = meta

    return jsonify(payload), status_code
