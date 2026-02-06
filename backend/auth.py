import os
import logging
from typing import Optional

from fastapi import Header, HTTPException

logger = logging.getLogger(__name__)

def _get_magic():
    secret_key = os.getenv("MAGIC_SECRET_KEY")
    if not secret_key:
        logger.error("MAGIC_SECRET_KEY is not set. Auth cannot validate tokens.")
        raise HTTPException(
            status_code=500,
            detail="Auth misconfigured: MAGIC_SECRET_KEY is not set on the backend.",
        )
    try:
        from magic_admin import Magic
    except Exception as exc:  # pragma: no cover - defensive import
        logger.exception("magic_admin SDK not installed or failed to import.")
        raise HTTPException(
            status_code=500,
            detail="Auth misconfigured: magic-admin SDK is not installed.",
        ) from exc
    return Magic(api_secret_key=secret_key)


def require_user(authorization: Optional[str] = Header(None)) -> str:
    """
    Validate Magic DID token and return the authenticated user email.
    """
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("Missing or invalid Authorization header.")
        raise HTTPException(status_code=401, detail="Missing auth token.")

    did_token = authorization.split(" ", 1)[1]
    try:
        magic = _get_magic()
        magic.Token.validate(did_token)
        metadata = magic.User.get_metadata_by_token(did_token)
        data = getattr(metadata, "data", None)
        email = data.get("email") if isinstance(data, dict) else None
        if not email:
            raise HTTPException(status_code=401, detail="User email not found.")
        return email
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Auth token validation failed.", exc_info=True)
        raise HTTPException(status_code=401, detail="Invalid auth token.") from exc
